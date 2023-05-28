import razorpay
from django.conf import settings
import numpy as np
import pytz
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.utils import timezone
import cv2
from datetime import datetime, timedelta
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
import csv
from .models import *

User = get_user_model()


@never_cache
def index(request):
    all_posts = Post.objects.all().order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
            username='admin').order_by("?")[:6]
    return render(request, "network/index.html", {
        "posts": posts,
        "suggestions": suggestions,
        "page": "all_posts",
        'profile': False
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            response = check_payment_expiry(request)
            if user.is_staff:
                if user.is_superuser:
                    return HttpResponseRedirect(reverse("admin:index"))
                else:
                    return HttpResponseRedirect(reverse("index"))
            else:
                return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        print(f"--------------------------Profile: {profile}----------------------------")
        cover = request.FILES.get('cover')
        print(f"--------------------------Cover: {cover}----------------------------")

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Check if profile pic has exactly one face
        if profile is not None:
            img = cv2.imdecode(np.fromstring(profile.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            img = cv2.resize(img, (800, 800))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier("network/haarcascade_frontalface_alt.xml")
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            if len(faces) < 1:
                return render(request, "network/register.html", {
                    "msg": "No faces detected. Upload a photo with a human face or try uploading a clear photo with "
                           "better lighting."
                })
            elif len(faces) > 1:
                return render(request, "network/register.html", {
                    "msg": "More than one face detecetd. (Upload a photo with only one person in it.)"
                })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = fname
            user.last_name = lname
            if profile is not None:
                user.profile_pic = profile
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            user.cover = cover
            user.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def cregister(request):
    if request.method == 'POST':
        user = request.user
        username = request.POST["username"]
        cname = request.POST["cname"]
        location = request.POST["location"]
        website = request.POST["website"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        profile = request.FILES.get("profile")
        print(f"--------------------------Profile: {profile}----------------------------")
        cover = request.FILES.get('cover')
        print(f"--------------------------Cover: {cover}----------------------------")

        if password == confirmation:
            if User.objects.filter(email=email).exists():
                return render(request, "network/c_register.html", {
                    "message": "Email already exists."
                })
        else:
            return render(request, "network/c_register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password, is_staff=True)
            if profile is not None:
                user.profile_pic = profile
                user.first_name = cname
            else:
                user.profile_pic = "profile_pic/no_pic.png"
            user.cover = cover
            user.save()
            company = Company(user=user, username=username, cname=cname, location=location, website=website,
                              email=email)
            company.save()
            Follower.objects.create(user=user)
        except IntegrityError:
            return render(request, "network/c_register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/c_register.html")


@never_cache
@login_required(login_url="/")
def profile(request, username):
    user = User.objects.get(username=username)
    all_posts = Post.objects.filter(creater=user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number == None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = []
    suggestions = []
    follower = False
    if request.user.is_authenticated:
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
            username='admin').order_by("?")[:6]

        if request.user in Follower.objects.get(user=user).followers.all():
            follower = True

    follower_count = Follower.objects.get(user=user).followers.all().count()
    following_count = Follower.objects.filter(followers=user).count()
    return render(request, 'network/profile.html', {
        "username": user,
        "posts": posts,
        "posts_count": all_posts.count(),
        "suggestions": suggestions,
        "page": "profile",
        "is_follower": follower,
        "follower_count": follower_count,
        "following_count": following_count
    })


@never_cache
@login_required(login_url="/")
def following(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values('user')
        all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
            username='admin').order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "following"
        })
    else:
        return HttpResponseRedirect(reverse('login'))


@never_cache
@login_required(login_url="/")
def saved(request):
    if request.user.is_authenticated:
        all_posts = Post.objects.filter(savers=request.user).order_by('-date_created')

        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number = 1
        posts = paginator.get_page(page_number)

        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
            username='admin').order_by("?")[:6]
        return render(request, "network/index.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "saved"
        })
    else:
        return HttpResponseRedirect(reverse('login'))


@never_cache
@login_required(login_url="/")
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        try:
            post = Post.objects.create(creater=request.user, content_text=text, content_image=pic)
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return HttpResponse(e)
    else:
        return HttpResponse("Method must be 'POST'")


@never_cache
@login_required(login_url="/")
@csrf_exempt
def edit_post(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        pic = request.FILES.get('picture')
        img_chg = request.POST.get('img_change')
        post_id = request.POST.get('id')
        post = Post.objects.get(id=post_id)
        try:
            post.content_text = text
            if img_chg != 'false':
                post.content_image = pic
            post.save()

            if (post.content_text):
                post_text = post.content_text
            else:
                post_text = False
            if (post.content_image):
                post_image = post.img_url()
            else:
                post_image = False

            return JsonResponse({
                "success": True,
                "text": post_text,
                "picture": post_image
            })
        except Exception as e:
            print('-----------------------------------------------')
            print(e)
            print('-----------------------------------------------')
            return JsonResponse({
                "success": False
            })
    else:
        return HttpResponse("Method must be 'POST'")


@csrf_exempt
def like_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def unlike_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.likers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def save_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.add(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def unsave_post(request, id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(pk=id)
            print(post)
            try:
                post.savers.remove(request.user)
                post.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def follow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(f".....................Follower: {request.user}......................")
            try:
                (follower, create) = Follower.objects.get_or_create(user=user)
                follower.followers.add(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def unfollow(request, username):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            user = User.objects.get(username=username)
            print(f".....................User: {user}......................")
            print(f".....................Unfollower: {request.user}......................")
            try:
                follower = Follower.objects.get(user=user)
                follower.followers.remove(request.user)
                follower.save()
                return HttpResponse(status=204)
            except Exception as e:
                return HttpResponse(e)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def comment(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            comment = data.get('comment_text')
            post = Post.objects.get(id=post_id)
            try:
                newcomment = Comment.objects.create(post=post, commenter=request.user, comment_content=comment)
                post.comment_count += 1
                post.save()
                print(newcomment.serialize())
                return JsonResponse([newcomment.serialize()], safe=False, status=201)
            except Exception as e:
                return HttpResponse(e)

        post = Post.objects.get(id=post_id)
        comments = Comment.objects.filter(post=post)
        comments = comments.order_by('-comment_time').all()
        return JsonResponse([comment.serialize() for comment in comments], safe=False)
    else:
        return HttpResponseRedirect(reverse('login'))


@csrf_exempt
def delete_post(request, post_id):
    if request.user.is_authenticated:
        if request.method == 'PUT':
            post = Post.objects.get(id=post_id)
            if request.user == post.creater:
                try:
                    delet = post.delete()
                    return HttpResponse(status=201)
                except Exception as e:
                    return HttpResponse(e)
            else:
                return HttpResponse(status=404)
        else:
            return HttpResponse("Method must be 'PUT'")
    else:
        return HttpResponseRedirect(reverse('login'))


@never_cache
@login_required(login_url="/")
def postjobs(request):
    if request.user.is_authenticated:
        following_user = Follower.objects.filter(followers=request.user).values('user')
        all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
        paginator = Paginator(all_posts, 10)
        page_number = request.GET.get('page')
        if page_number is None:
            page_number = 1
        posts = paginator.get_page(page_number)
        followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
        suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
            username='admin').order_by("?")[:6]
        jobs = JobPosting.objects.filter(company=request.user.username).order_by('-created_at')
        return render(request, "network/postjobs.html", {
            "posts": posts,
            "suggestions": suggestions,
            "page": "postjobs",
            "jobs": jobs
        })
    return HttpResponseRedirect(reverse('network/postjobs.html'))


@never_cache
@login_required(login_url="/")
def jobposting(request):
    user_object = User.objects.get(username=request.user.username)
    company_object = Company.objects.get(user=user_object)

    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.user
        location = request.POST.get('location')
        description = request.POST.get('description')
        qualifications = request.POST.get('qualifications')
        requirements = request.POST.get('requirements')
        responsibilities = request.POST.get('responsibilities')
        email = user_object.email
        website = request.POST.get('website')
        salary = request.POST.get('salary')

        job_posting = JobPosting.objects.create(title=title, company=company, location=location,
                                                description=description, qualifications=qualifications,
                                                requirements=requirements, responsibilities=responsibilities,
                                                email=email,
                                                website=website, salary=salary)
        return redirect('postjobs')

    return redirect(request, 'postjobs')


@never_cache
@login_required(login_url="/")
def job_delete(request, jid):
    job = get_object_or_404(JobPosting, jid=jid, company=request.user.username)
    if request.method == 'POST':
        job.delete()
        return redirect('postjobs')
    context = {'job': job}
    return render(request, 'postjobs.html', context)


@never_cache
@login_required(login_url="/")
def job_edit(request, jid):
    job = get_object_or_404(JobPosting, jid=jid, company=request.user.username)
    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.location = request.POST.get('location')
        job.description = request.POST.get('description')
        job.qualifications = request.POST.get('qualifications')
        job.requirements = request.POST.get('requirements')
        job.responsibilities = request.POST.get('responsibilities')
        job.website = request.POST.get('website')
        job.salary = request.POST.get('salary')
        job.save()
        return redirect('postjobs')
    context = {'job': job}
    return render(request, 'postjobs.html', context)


@never_cache
@login_required(login_url="/")
def userjobs(request):
    following_user = Follower.objects.filter(followers=request.user).values('user')
    all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
    suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
        username='admin').order_by("?")[:6]
    jobs = JobPosting.objects.all().order_by('-created_at')
    job_list = []
    try:
        active_payment = Payment.objects.filter(user=request.user, has_expired=False).latest('expiry_date')
    except Payment.DoesNotExist:
        active_payment = 0
    for job in jobs:
        cmpny = job.company
        user = User.objects.filter(username=cmpny).first()
        if user:
            profile_pic_urls = user.profile_pic.url
        else:
            profile_pic_urls = None
        applied = False
        if request.user.is_authenticated:
            # Check if the user has already applied to this job
            applied = JobApplication.objects.filter(job_posting=job, email=request.user.email).exists()
            job_list.append({"job": job, "profile_pic_url": profile_pic_urls, "applied": applied})
        else:
            job_list.append({"job": job, "profile_pic_url": profile_pic_urls})
    return render(request, 'network/userjobs.html', {
        "suggestions": suggestions,
        "job_list": job_list,
        "page": "userjobs",
        "active_payment": active_payment,
    })


@never_cache
@login_required(login_url="/")
def jobapplication(request, jid):
    following_user = Follower.objects.filter(followers=request.user).values('user')
    all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
    suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
        username='admin').order_by("?")[:6]
    resume_error = None

    job_posting = get_object_or_404(JobPosting, jid=jid)

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        resume = request.FILES['resume']
        cover_letter = request.POST['cover_letter']
        job_posting_id = request.POST['job_posting']
        job_posting = get_object_or_404(JobPosting, jid=job_posting.jid)

        if not resume.name.endswith('.pdf'):
            resume_error = 'Invalid file type. Please upload a PDF file.'
        else:
            job_application = JobApplication(
                name=name,
                email=email,
                phone=phone,
                resume=resume,
                cover_letter=cover_letter,
                job_posting=job_posting,
            )
            job_application.save()

            return redirect('userjobs')

    return render(request, 'network/jobapplication.html', {
        "suggestions": suggestions,
        "page": "userjobs",
        "resume_error": resume_error
    })


@never_cache
@login_required(login_url="/")
def jobapplicants(request, jid):
    following_user = Follower.objects.filter(followers=request.user).values('user')
    all_posts = Post.objects.filter(creater__in=following_user).order_by('-date_created')
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    if page_number is None:
        page_number = 1
    posts = paginator.get_page(page_number)
    followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
    suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
        username='admin').order_by("?")[:6]

    job_posting = JobPosting.objects.get(jid=jid)
    job_applications = job_posting.applications.all()

    for job_application in job_applications:
        try:
            user = User.objects.get(email=job_application.email)
            job_application.user = user
        except User.DoesNotExist:
            pass

    return render(request, 'network/jobapplicants.html', {
        "suggestions": suggestions,
        "page": "postjobs",
        "job_applications": job_applications
    })


@never_cache
@login_required(login_url="/")
def download_csv(request, jid):
    job_posting = JobPosting.objects.get(jid=jid)
    job_applications = job_posting.applications.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="Job applications for {job_posting.title}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Cover Letter', 'Resume URL'])

    for job_application in job_applications:
        writer.writerow(
            [job_application.name, job_application.email, job_application.phone, job_application.cover_letter,
             job_application.resume.url])

    return response


@never_cache
@login_required(login_url="/")
def search(request):
    return render(request, 'network/user_search.html', {
        "page": "search",
    })


# RAZORPAY_API_KEY = "rzp_test_V76tEmQszdzu8t"
# RAZORPAY_API_SECRET = "FmoMelanxKZZbIlXs9lQO1Eg"

@never_cache
@login_required(login_url="/")
@csrf_exempt
def payment(request):
    followings = Follower.objects.filter(followers=request.user).values_list('user', flat=True)
    suggestions = User.objects.exclude(pk__in=followings).exclude(username=request.user.username).exclude(
        username='admin').order_by("?")[:6]
    active_payment = request.user.payment_set.filter(has_expired=False).first()
    if active_payment:
        payments = request.user.payment_set.all()
        return render(request, 'network/payment_details.html', {
            'page': 'payment',
            "suggestions": suggestions,
            'payments': payments
        })

    return render(request, "network/payment.html")


@never_cache
@login_required(login_url="/")
@csrf_exempt
def confirm_payment(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('payment_id')
        type = request.POST.get('type')
        razorpay_client = razorpay.Client(auth=("rzp_test_V76tEmQszdzu8t", "FmoMelanxKZZbIlXs9lQO1Eg"))
        payment = razorpay_client.payment.fetch(razorpay_payment_id)
        subscription = get_object_or_404(Subscription, subscription_type=type)
        payment_obj = Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=float(subscription.amount),
            payment_id=razorpay_payment_id,
            payment_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=subscription.duration_in_days),
        )

        subscription.has_active_payment = True
        subscription.save()
        if payment['status'] == 'authorized':
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'failure'})


def check_payment_expiry(request):
    user = request.user
    payments = Payment.objects.filter(user=user)

    if payments:
        most_recent_payment = payments.latest('payment_date')
        today = timezone.now().astimezone(pytz.timezone('Asia/Kolkata'))
        if most_recent_payment.expiry_date < today:
            most_recent_payment.has_expired = True
            most_recent_payment.save()
            return 'payment expired'
        return 'payment not expired'

    return 'no payments'


@never_cache
@login_required(login_url="/")
def editprofile(request):
    user = request.user
    current_password_error = ''
    current_cover_url = user.cover.url if user.cover else None
    if request.method == 'POST':
        username = request.POST["username"]
        email = request.POST["email"]
        fname = request.POST["firstname"]
        lname = request.POST["lastname"]
        profile = request.FILES.get("profile")
        cover = request.FILES.get('cover')

        if profile is not None:
            img = cv2.imdecode(np.fromstring(profile.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            img = cv2.resize(img, (800, 800))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier("network/haarcascade_frontalface_alt.xml")
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            if len(faces) < 1:
                return render(request, "network/editprofile.html", {
                    "msg": "No faces detected. Upload a photo with a human face or try uploading a clear photo with "
                           "better lighting."
                })
            elif len(faces) > 1:
                return render(request, "network/editprofile.html", {
                    "msg": "More than one face detected. Upload a photo with only one person in it."
                })

        user.username = username
        user.email = email
        user.first_name = fname
        user.last_name = lname

        if profile is not None:
            user.profile_pic = profile

        if cover is not None:
            user.cover = cover

        user.save()
        return redirect('profile', user.username)

    else:
        return render(request, 'network/editprofile.html', {'current_cover_url': current_cover_url})


def cpass(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = request.user
        if user.check_password(current_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()

                updated_user = authenticate(request, username=user.username, password=new_password)
                if updated_user is not None:
                    login(request, updated_user)

                messages.success(request, 'Password changed successfully.')
                return redirect('cpass')
            else:
                messages.error(request, 'New password and confirm password do not match.')
        else:
            messages.error(request, 'Current password is incorrect.')

    return render(request, 'network/change_password.html')
