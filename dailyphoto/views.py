
from django.http  import  HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth import get_user_model


from .forms import LikeForm, PostForm, CustomUserChangeForm, ProfileForm, CommentForm
from .models import Post, Comment, Profile, Like, User
from . import models
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q

# 주소 index 
def index(request):
  """
  dailyphoto 게시물 출력
  """

    # 조회
  post_list = Post.objects.order_by('-create_date')      
  user = get_user_model()
  follow_list= user.objects.filter(followers=request.user)

  
  
  q = Q(author=request.user)
  if (follow_list.count()>0):
    for my_following in follow_list:
      q.add(Q(author=my_following),q.OR)

  post_list = Post.objects.filter(q).order_by('-create_date')

  all_users = list(user.objects.values_list('username'))
  print(all_users)
  all_users = list(user.objects.values_list('username')[0])
  print(all_users)
  all_users = list(user.objects.values_list('username').values('username'))
  print(all_users)
  # all_users=list(user.objects.values['username'])
  # print(all_users)
  # all_users = list(user.objects.values_list('username').get('username'))
  # print(all_users)

  # all_users = list(user.objects.values_list('username').values('username'))
  # print(all_users)

  all_users = list(user.objects.values('username'))
  print(all_users)
  user_list = []
  for us in all_users:
    user_list.append(us['username'])

  print(user_list)

  # all_users=user.objects.values('username')
  # print(all_users)
  # all_users=list(all_users)
  # print(all_users)


  
  comment_form = CommentForm()

  context = {'post_list': post_list,  "comment_form" : comment_form,'user_list':user_list}
  return render(request, 'dailyphoto/post_list.html', context)

# 검색기능 
def search(request):
  post_list = Post.objects.all()

  user = get_user_model()
  follow_list= user.objects.filter(followers=request.user)
  
  q = Q(author=request.user)
  if (follow_list.count()>0):
    for my_following in follow_list:
      q.add(Q(author=my_following),q.OR)


  post_list = Post.objects.filter(q).order_by('-create_date')
  
  search = request.GET.get('search','')
  if search:
     post_list = post_list.filter(
      Q(create_date__icontains = search) 
    )
  comment_form = CommentForm

  return render(request, 'dailyphoto/post_list.html', {'post_list':post_list, 'search':search, 'comment_form':comment_form})


# post 상세
def detail(request, id):
  
  post  = get_object_or_404(Post, pk=id) # 예외일때 404에러 발생
  # get_object_or_404 <- 오류 화면 구성
  context = {'post': post}
  return render(request, 'dailyphoto/post_detail.html', context)
  

@login_required(login_url='common:login')
def comment_create(request, post_id):
  if request.user.is_authenticated:

    post = get_object_or_404(models.Post, pk=post_id)

    form = CommentForm(request.POST)
    if form.is_valid():
      comment = form.save(commit=False)
      comment.author = request.user
      comment.post = post
      comment.save()
      
      return redirect(reverse('dailyphoto:index')+"#comment-"+str(comment.id))

    else:
      return render(request, 'dailyphoto/post_list.html')
                  

def comment_delete(request, comment_id):
    if request.user.is_authenticated:
        comment = get_object_or_404(models.Comment, pk=comment_id)
        if request.user == comment.author:
            comment.delete()

        return redirect(reverse('dailyphoto:index'))

    else:
        return render(request, 'dailyphoto/post_list.html')
      

# 글 업로드 함수
# @login_required(login_url='common:login')
def post_create(request): 
  """
  upload
  """

  if request.method== "POST":
    print('request method is post')
    print(request.POST)
    form = PostForm(request.POST)
    if form.is_valid():
      post = form.save(commit=False)  

      # title이 입력되지 않으면 현재날짜를 title로 넣어줌
      if post.title == None:
        post.title=timezone.localdate()

      # photo가 입력되었는지 확인하고 넣어줌
      if 'photo' in request.FILES:
        post.photo=request.FILES['photo']
      else:
        pass

      # 리스트로 입력된 icons를 스트링으로 변환해서 필드에 넣어줌
      icons = request.POST.getlist('icons[]')
      post.icons='&'.join(icons)
      post.author= request.user
      post.create_date=timezone.now()
      post.save()
      print('post save made')
      return redirect('dailyphoto:index')

    else:
      print('form is not valid')

  else:
    print('request method is get -upload')
    form=PostForm()
    
  context = {'form': form }
  return render(request, 'dailyphoto/upload_page.html', context )


#글 수정
def post_update(request,post_id):
  if request.method== "POST":
    form = PostForm(request.POST)
    # print(form)
    context = {'form': form}
    if form.is_valid():
      post = get_object_or_404(models.Post, pk=post_id)
      # post_before = post
      post_temp = form.save(commit=False)

      # title이 입력
      if post_temp.title != None:
        post.title=post_temp.title

      # photo 입력
      if 'photo' in request.FILES:
        post.photo=request.FILES['photo']
      else:
        pass
      
      #content
      post.content=post_temp.content

      # 리스트로 입력된 icons를 스트링으로 변환해서 필드에 넣어줌
      icons = request.POST.getlist('icons[]')
      post.icons='&'.join(icons)

      #
      post.author= request.user
      # post.like_count=post_temp.like_count
      # post.create_date=post_temp.creat_date
      post.modify_date=timezone.now()

      post.save()
      print('post update made')

      return redirect('dailyphoto:index')
    else:
      print('post update - form is not valid')
      print(request)
      print(form)
    
  else:
    print('request method is get')
    post = get_object_or_404(models.Post, pk=post_id)
    print(post)
    print(post.content)
    form = PostForm(instance=post)
    print(form)
    context = {'form': form ,'post':post}
    if form.is_valid():
      print('get update - form is valid')
      return render(request, 'dailyphoto/update_page.html', context )  

    else:
      print('get update - form is not valid')
      # form = PostForm(request.POST)
      # print(form)
      
      # form = PostForm(request.GET)
      # print(form)
      context = {'form': form }
  
  return render(request, 'dailyphoto/update_page.html', context )


  

#글 삭제
def post_delete(request,post_id):
  if request.method== "GET":
    print('request method is get.')
    post = get_object_or_404(models.Post, pk=post_id)
    form = PostForm(request.POST)
    if form.is_valid():
      print('form is valid -delete')
      post.delete()
    else:
      print('post delete - form is not valid')
  return redirect('dailyphoto:index')


#like
@login_required(login_url='common:login')
def like(request):

  def liking(post, like,like_count):
    like.post=post
    post.like_count = like_count + 1
    print(like)
    like.save()
    post.save()
    print('liked')

  if request.method=="POST":
    form = LikeForm(request.POST)
    
    print(request.body)
    if form.is_valid():
      like=form.save(commit=False)
      like.author= request.user
      data=request.body.decode()
      data = data.split('&')
      data_post=data[0].split('=')[1]
      post = get_object_or_404(models.Post, pk=data_post)
      post_filtered = Like.objects.filter(post_id = data_post)
      if post_filtered:
        user_filtered = post_filtered.filter(author_id=request.user)
        if user_filtered :
          print('double liking error')
        else:
          like_count=post_filtered.count()
          liking(post,like,like_count)
      else:
        like_count=post_filtered.count()
        liking(post,like,like_count)
    else:
      print('form is not valid')
  else:
    print('else')
    print(request)

  return HttpResponse()

# like 취소
@login_required(login_url='common:login')
def unlike(request):

  if request.method=="POST":
    form = LikeForm(request.POST)
    
    print(request.body)
    if form.is_valid():
      data=request.body.decode()
      data = data.split('&')
      data_post=data[0].split('=')[1]
      post = get_object_or_404(models.Post, pk=data_post)
      post_filtered = Like.objects.filter(post_id = data_post)
      if post_filtered:
        user_filtered = post_filtered.filter(author_id=request.user)
        if user_filtered :
          print('like data exist')
          like = user_filtered.first()
          print(like)
          like.delete()
          post.like_count = post_filtered.count() -1
          post.save()
        else:
          pass
      else:
        pass
    else:
      print('form is not valid')
  else:
    print('else')
    print(request)

  return HttpResponse()

#프로필화
def profile(request, username):
    # person = get_object_or_404(get_user_model(), username = username )
    user = get_user_model()
    person = user.objects.filter(username=username).first()
    
    if person :
      post_photo = Post.objects.filter(author_id = person.id).order_by('-create_date')

      context = {
        'person': person,
        'post_photo' : post_photo
        }

      url='dailyphoto/profile.html'
      return render(request, url, context)
    else:
      return redirect('dailyphoto:index')


def modify_profile(request):
    if request.method == 'POST':
      user_change_form = CustomUserChangeForm(request.POST, instance=request.user)
      profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
      if user_change_form.is_valid() and profile_form.is_valid():
          user = user_change_form.save()
          profile_form.save()
          return redirect('dailyphoto:profile', user.username)
      return redirect('dailyphoto:profile')
    else:
        user_change_form = CustomUserChangeForm(instance=request.user)
        profile, create = Profile.objects.get_or_create(user=request.user)
        profile_form = ProfileForm(instance=profile)
        return render(request, 'dailyphoto/profile_form.html', {
            'user_change_form': user_change_form,
            'profile_form': profile_form
        })


def follow(request, user_pk):
    if request.user.is_authenticated:
        user = get_user_model()
        person = get_object_or_404(user, pk=user_pk)
        if person != request.user:
            # if request.user.followings.filter(pk=user_pk).exists():
            if person.followers.filter(pk=request.user.pk).exists():
                person.followers.remove(request.user)
            else:
                person.followers.add(request.user)
        return redirect('dailyphoto:profile', person.username)
    return redirect('dailyphoto:login')

