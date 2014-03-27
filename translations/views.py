from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import RequestContext, loader
from django.core.urlresolvers import reverse
from django.views import generic
from translations.models import Article, Language, Linguini_Translation, Sentence, Language_Proficiency, Translation_Attempt, Translation_Chunk
from datetime import datetime
from nltk import tokenize
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
import random


def site_login(request):

    if request.POST:
        try:
            username = request.POST['username']
            password = request.POST['password']

        except (KeyError):
            return render(request, 'translations/login.html', {
                'error_message' : "Incomplete form submitted.",
                })
        else:
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                    #User is valid, active and authenticated
                    login(request, user)
                    return HttpResponseRedirect(reverse('translations:home'))
            else:
                # the authentication system was unable to verify the username and password
                return render(request, 'translations/login.html', {'error_message': "Username/password is incorrect"})
    else:
        return render(request, 'translations/login.html', {})

@login_required
def site_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


@login_required
def home(request):
    user = request.user
    name = user.first_name + ' ' + user.last_name
    language_profs = Language_Proficiency.objects.filter(user=request.user)


    return render(request, 'translations/home.html', {'name': name, 'language_profs':language_profs})

@user_passes_test(lambda u: u.is_staff, login_url="/translations/access-denied/")
def new_article(request):
    languages = Language.objects.all().order_by('name')
    difficulties = Article.DIFFICULTY_CHOICES

    return render(request, 'translations/new-article.html', {'languages':languages, 'difficulties': difficulties})

#locals

@user_passes_test(lambda u: u.is_staff, login_url="/translations/access-denied/")
def submit_new_article(request):
    try:
        article_name = request.POST['article-name']
        article_source = request.POST['article-source']
        article_url = request.POST['article-url']
        article_difficulty = request.POST['article-difficulty']
        article_content = request.POST['article-content']
        article_origin_language = request.POST['article-origin-language']
        article_desired_languages = request.POST.getlist('article-desired-language')

    except (KeyError):
        #Redisplay the article creation form
        return render(request, 'translations/new-article.html', {
            'error_message' : "You didn't select a choice.",
            })
    else:
        new_article = Article.objects.create(name=article_name, content_source=article_source, source_url=article_url,
                                    difficulty=article_difficulty, content=article_content, origin_language_id=article_origin_language,
                                    date_added=datetime.now(), submitted_by_id=1)

        content_sentences = tokenize.sent_tokenize(article_content)

        for desired_language_id in article_desired_languages:
            desired_translation = Linguini_Translation.objects.create(article=new_article, desired_language_id=desired_language_id)
            for sentence in content_sentences:
                Sentence.objects.create(linguini_trans=desired_translation, original=sentence)

        return HttpResponseRedirect(reverse('translations:article_list'))

@user_passes_test(lambda u: u.is_staff, login_url="/translations/access-denied/")
def article_detail(request, pk):
    try:
        article = Article.objects.get(pk=pk)

    except (KeyError, Article.DoesNotExist):
        #Redisplay the article creation form
        return render(request, 'translations/article-detail.html', {
            'error_message' : "Article doesn't exist.",
            })
    else:
        desired_languages = Language.objects.filter(linguini_translation__article=article)
        linguini_trans = Linguini_Translation.objects.filter(article=article)[0]
        sentences = Sentence.objects.filter(linguini_trans = linguini_trans).order_by('id')

    return render(request, 'translations/article-detail.html', {'article':article, 'desired_languages':desired_languages, 'sentences':sentences})

def register(request):
    if request.POST:
        try:
            username = request.POST['username']
            password = request.POST['password']
            confirm_password = request.POST['confirm-password']
            first_name = request.POST['first-name']
            last_name = request.POST['last-name']
            email_address = request.POST['email-address']
            known_languages = request.POST.getlist('user-languages')


        except (KeyError):
            return render(request, 'translations/register.html', {
                'error_message' : "Incomplete form submitted.",
                })
        else:

            required_fields = [username, password, first_name, last_name, email_address]

            if not all(field.strip() != '' for field in required_fields):
                error_message = "Required field(s) missing."
            else:
                if password != confirm_password:
                    error_message = "Passwords don't match."
                else:
                    if User.objects.filter(username=username).exists():
                        error_message = "Username is already in use"
                    else:
                        user = User.objects.create_user(username, email_address, password)
                        user.first_name = first_name
                        user.last_name = last_name
                        user.save()

                        for language_id in known_languages:
                            language = Language.objects.get(id=language_id)
                            pr = Language_Proficiency(user=user, language=language)
                            pr.save()

                        user = authenticate(username=username, password=password)

                        if user is not None and user.is_active:
                            #User is valid, active and authenticated
                            login(request, user)

                            return HttpResponseRedirect(reverse('translations:language-prof'))

            languages = Language.objects.all().order_by('name')
            return render(request, 'translations/registration.html', {'error_message' : error_message, 'languages':languages})

    else:
        languages = Language.objects.all().order_by('name')

        return render(request, 'translations/registration.html', {'languages':languages})

@login_required
def language_prof(request):
    if request.POST:
        try:
            language_profs = []
            for language_prof_key in [key for key in request.POST.keys() if key.startswith('language-proficiency-id-')]:
                language_profs.append([language_prof_key.split('-')[3],request.POST[language_prof_key]])

            #print language_profs

        except (KeyError):
            return render(request, 'translations/language-prof.html', {
                'error_message' : "Incomplete form submitted.",
                })
        else:
            for language_prof in language_profs:
                lang_prof_obj = Language_Proficiency.objects.get(language__id=language_prof[0], user=request.user)
                #print lang_prof_obj.language.name
                lang_prof_obj.proficiency = language_prof[1]
                lang_prof_obj.save()

            return HttpResponseRedirect(reverse('translations:home'))


    else:
        languages = Language.objects.filter(language_proficiency__user=request.user)
        proficiency_choices = Language_Proficiency.PROFICIENCY_CHOICES
        return render(request, 'translations/language-prof.html', {'proficiency_choices': proficiency_choices,'languages':languages})

@login_required
def user_translate(request, origin_pk, dest_pk):
    if request.POST:
        try:
            sentence_ids = request.POST.getlist('sentence_id')
            translation_text = request.POST['translation-text']

        except (KeyError):
            return render(request, 'translations/language-prof.html', {
                'error_message' : "Incomplete form submitted.",
                })

        else:
            translation_text = translation_text.strip()
            if translation_text == "":
                error_message = "No translation provided."
            else:
                translated_sentences = tokenize.sent_tokenize(translation_text) # split sentences

                if len(translated_sentences) != len(sentence_ids):
                    error_message = "Too many or too few sentences. Please input the same number of sentences as the provided text"
                else:
                    sentence_ids.sort()

                    translation_chunk = Translation_Chunk.objects.create(user=request.user, translation=translation_text,
                                                    date_submitted=datetime.now(), num_sent=len(sentence_ids))

                    for sentence_id, trans_sent in zip(sentence_ids, translated_sentences):
                        sentence = Sentence.objects.get(id=sentence_id)
                        translation_chunk.sentences.add(sentence)
                        trans_attempt = Translation_Attempt.objects.create(user=request.user, sentence=sentence,
                                                translation=trans_sent, date_submitted=datetime.now())
                        update_sentence(sentence_id)

                    translation_chunk.save()

                    if 'trans_count' not in request.session:
                        request.session['trans_count'] = {}

                    if str(origin_pk) not in request.session['trans_count']:
                        request.session['trans_count'][str(origin_pk)] = {}

                    if str(dest_pk) not in request.session['trans_count'][str(origin_pk)]:
                        request.session['trans_count'][str(origin_pk)][str(dest_pk)] = 0

                    request.session['trans_count'][str(origin_pk)][str(dest_pk)] = request.session['trans_count'][str(origin_pk)][str(dest_pk)] + 1
                    request.session.modified = True

                    #print request.session['trans_count'][str(origin_pk)][str(dest_pk)]

                    return HttpResponseRedirect(reverse('translations:user-translate', args=(origin_pk,dest_pk,)))


    else:

        try:
            origin_language_prof = Language_Proficiency.objects.get(language__id=origin_pk, user=request.user)
            dest_language_prof = Language_Proficiency.objects.get(language__id=dest_pk, user=request.user)
        except(Language_Proficiency.DoesNotExist):
            error_message = "Chosen language does not exist, or is not associated with the current user"
        else:

            if 'trans_count' in request.session:
                if str(origin_pk) in request.session['trans_count']:
                    if str(dest_pk) in request.session['trans_count'][str(origin_pk)]:
                        if request.session['trans_count'][str(origin_pk)][str(dest_pk)] >= 8:
                            return render(request, 'translations/user-translate.html', 
                                {'error_message':"You have reached your session limit for this language. In order to translate more sentences, please logout and log back in", 'origin_language_prof':origin_language_prof,
                                'dest_language_prof':dest_language_prof})


            final_chunk = Chunk_Holder(0)

            # Determine the proficiency of the user and which difficulties will be available for them as such

            prof_choices = [each_list[0] for each_list in Language_Proficiency.PROFICIENCY_CHOICES]
            proficiency = min(2, min(prof_choices.index(origin_language_prof.proficiency), prof_choices.index(dest_language_prof.proficiency)))

            diff_choices = [each_list[0] for each_list in Article.DIFFICULTY_CHOICES]
            if proficiency >= 2:
                article_diffs = diff_choices
            else:
                article_diffs = diff_choices[:proficiency + 1]

            #print article_diffs
            #print proficiency

            num_sent = random.randint(1,5) # random chunk size

            # filter sentences by origin language, desired language, and difficulty.
            # exclude sentences that have already been translated by user
            # order by pk
            sentences = Sentence.objects.filter(linguini_trans__article__origin_language__id=origin_pk,
                linguini_trans__desired_language__id=dest_pk,
                 linguini_trans__article__difficulty__in = article_diffs).exclude(translation_attempt__user=request.user).order_by('id')

            if sentences.exists():

                #organize sentences into continuous chunks

                trans_chunks = []
                last_trans_id = sentences[0].linguini_trans.id
                last_sent_id = sentences[0].id
                chunk = Chunk_Holder(last_trans_id)
                chunk.add(sentences[0])

                for sent in sentences[1:]:
                    if sent.id == last_sent_id + 1 and sent.linguini_trans.id == last_trans_id:
                        chunk.add(sent)
                    else:
                        trans_chunks.append(chunk)
                        chunk = Chunk_Holder(sent.linguini_trans.id)
                        chunk.add(sent)

                    last_trans_id = sent.linguini_trans.id
                    last_sent_id = sent.id

                trans_chunks.append(chunk)

                # check chunks to find eligible ones (=> desired chunk size)
                # if no eligible chunks are found, the desired chunk size is decremented by one
                # until at least one eligible chunk is found

                chunk_found = False
                eligible_chunks = []
                #print num_sent

                for x in range(num_sent,0,-1):
                    for trans_chunk in trans_chunks:
                        if trans_chunk.count >= x:
                            chunk_found = True
                            eligible_chunks.append(trans_chunk)
                            num_sent_adjusted = x
                    if chunk_found:
                        break

                if chunk_found == False:
                    print "ERROR: Chunk should always be found"


                final_chunk = random.choice(eligible_chunks) #randomly choose from the eligible chunks
                #print eligible_chunks



            if sentences.exists():

                # chunks may be bigger than desired chunk size
                # code chooses random subselection of larger chunks

                start_index = random.randint(0, final_chunk.count - num_sent_adjusted)
                end_index = start_index + num_sent_adjusted

                #print "Start: %i; End: %i" % (start_index, end_index)

                if end_index >= final_chunk.count:
                    sentences = final_chunk.sentences[start_index:]
                else:
                    sentences = final_chunk.sentences[start_index: end_index]

                return render(request, 'translations/user-translate.html',
                 {'sentences':sentences, 'origin_language_prof':origin_language_prof,
                  'dest_language_prof':dest_language_prof})
            else:
                return render(request, 'translations/user-translate.html',
                 {'error_message':"No further selections for this language combination are available to be translated.", 'origin_language_prof':origin_language_prof,
                  'dest_language_prof':dest_language_prof})


class Chunk_Holder:
    def __init__(self, trans_id):
        self.trans_id = trans_id
        self.sentences = []
        self.count = 0
    def add(self, x):
        self.sentences.append(x)
        self.count += 1
    def __str__(self):
        return "Chunk [trans_id: %i, count: %i]" % (self.trans_id, self.count)


def update_sentence(sentence_id):
    try:
        sentence = Sentence.objects.get(id=sentence_id)
    except(Sentence.DoesNotExist):
        pass
    else:
        if sentence.translation_is_choosen:
            pass
        else:
            threshold = sentence.linguini_trans.acceptance_threshold
            sent_cnts = []

            all_translation_attempts = sentence.translation_attempt_set.all()

            for attempt in all_translation_attempts:
                count = 1
                for comp_attempt in all_translation_attempts:
                    if comp_attempt.translation == attempt.translation:
                        count += 1
                sent_cnts.append(count)

            max_count = max(sent_cnts)


            if max_count >= threshold:
                sentence.translation_is_choosen = True
                sentence.attempts_before_acceptance = len(all_translation_attempts)
                sentence.best_attempt = all_translation_attempts[sent_cnts.index(max_count)]
                sentence.accepted_translation = sentence.best_attempt
            else:
                sentence.best_attempt = all_translation_attempts[sent_cnts.index(max_count)]

            sentence.save()

    return





class ArticleView(generic.DetailView):
    model = Article
    template_name = 'translations/article-detail.html'

class ArticleListView(generic.ListView):
    template_name = 'translations/article-list.html'

    def get_queryset(self):
        """Return the last five published polls."""
        return Article.objects.order_by('-date_added')


class DirectTemplateView(generic.TemplateView):
    extra_context = None
    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        if self.extra_context is not None:
            for key, value in self.extra_context.items():
                if callable(value):
                    context[key] = value()
                else:
                    context[key] = value
        return context


def delete_article(article_id):

    # get article by ID
    # figure out what gets deleted based on db relationships

    pass
