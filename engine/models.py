import csv

from django.db import models
from django.db import transaction
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from ckeditor.fields import RichTextField
from django.utils.safestring import mark_safe

from .constants import *

from django.contrib.auth.models import User

class Logs_B(models.Model):
   mobile_number = models.TextField(
                            null=True,
                            blank=True)
   icici_user_id = models.TextField(
                            null=True,
                            blank=True)
   query = models.TextField(
                            null=True,
                            blank=True)
   time = models.DateTimeField(auto_now_add=True)
   chatbot_answer = models.TextField(
                                     null=True,
                                     blank=True)

class Logs_IT(models.Model):
   alexa_id = models.TextField(
                            null=True,
                            blank=True)

   device_id = models.TextField(
                            null=True,
                            blank=True)

   access_token = models.TextField(
                            null=True,
                            blank=True)

   query = models.TextField(
                            null=True,
                            blank=True)
   time = models.DateTimeField(auto_now_add=True)    
   
   chatbot_answer = models.TextField(
                                     null=True,
                                     blank=True)
   icici_user_id = models.TextField(
                            null=True,
                            blank=True)
   request_packets_fired = models.TextField(
                            null=True,
                            blank=True)
   response_packets_fired = models.TextField(
                            null=True,
                            blank=True)

   latency = models.FloatField(null=True, blank=True)
   
class BusinessUser(User):

   def save(self, *args, **kwargs):

       self.set_password(self.password)
       super(BusinessUser, self).save(*args, **kwargs)

   class Meta:
       verbose_name = "Business User"
       verbose_name_plural = "Business Users"

class ITUser(User):

   def save(self, *args, **kwargs):

       self.set_password(self.password)
       super(ITUser, self).save(*args, **kwargs)

   class Meta:
       verbose_name = "IT User"
       verbose_name_plural = "IT Users"

class VelocityChanges(models.Model):
    velocity_name = models.TextField(
                             null=True,
                             blank=True)

    velocity_time = models.TextField(
                             null=True,
                             blank=True)

    velocity_times = models.TextField(
                             null=True,
                             blank=True)

    velocity_amount = models.TextField(
                             null=True,
                             blank=True)

class VelocityLogs(models.Model):
    velocity_id = models.TextField(
                             null=True,
                             blank=True)

    mobile_number = models.TextField(
                             null=True,
                             blank=True)

    time_created = models.DateTimeField(auto_now_add=True)
    
class UserPipe(models.Model):
    user_id = models.CharField(max_length=100,
                               null=False,
                               blank=False)
    pipe = models.TextField(null=False,
                            blank=False)

    def __str__(self):
        return self.user_id + " " + " " + " " + self.pipe

class AnalyticCount(models.Model):
    intent = models.ForeignKey('Intent',
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    entity = models.ForeignKey('Entities',
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)
    time = models.DateField(auto_now=True)

    def __str__(self):
        return str(self.time)


class Language(models.Model):
    name = models.TextField(
                            null=True,
                            blank=True,
                            default="eng")

    def __str__(self):
        return self.name


class Channel(models.Model):
    name = models.TextField(
                            null=True,
                            blank=True,
                            default="web")

    def __str__(self):
        return self.name


class ChannelSentences(models.Model):
    group_of_sentences = models.ManyToManyField('Sentences',
                                                blank=True)

    name = models.TextField(
                            null=True,
                            blank=True)

    def __str__(self):
        if self.group_of_sentences.all().count()>0:
            return mark_safe(self.group_of_sentences.all()[0].sentence)
        else:
            return "AA"
    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Channel Sentences'
        verbose_name_plural = 'Channel Sentences'


class Sentences(models.Model):
    sentence = RichTextField(config_name='default')
    language = models.ForeignKey('Language',
                                 null=True,
                                 blank=True,
                                 
                                 on_delete=models.CASCADE)
    channel = models.ForeignKey('Channel',
                                null=True,
                                blank=True,
                               
                                on_delete=models.CASCADE)
    file = models.ForeignKey('Files',
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)

    def __str__(self):
        return mark_safe(self.sentence)

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Sentences'
        verbose_name_plural = 'Sentences'


class AutoCorrectWordList(models.Model):
    word = models.TextField(
                            null=False,
                            blank=False)

    def __str__(self):
        return self.word

    class Meta:
        verbose_name = 'Autocorrect Word List'
        verbose_name_plural = 'Autocorrect Word List'


class QueryFeedbackCounter(models.Model):
    user = models.ForeignKey('Profile',
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)
    query = models.ForeignKey('QueryCnt',
                              null=True,
                              blank=True,
                              on_delete=models.CASCADE)

    like_cnt = models.IntegerField(default=0)

    dislike_cnt = models.IntegerField(default=0)

    def __str__(self):
        return self.user.user_id + " " + self.query.query + " " + str(self.like_cnt) + " " + str(
            self.dislike_cnt)

    class Meta:
        verbose_name = 'Query Feedback'
        verbose_name_plural = 'Query Feedback'


class Variables(models.Model):
    variable_name = models.TextField(null=False,
                                     blank=False)

    variable_value = models.TextField(null=False,
                                      blank=False)

    def __str__(self):
        return self.variable_name + " " + self.variable_value

class SysConfig(models.Model):
    api_ip = models.TextField(null=True,
                              blank=True)

    api_port = models.TextField(null=True,
                                blank=True)


class Config(models.Model):
    question_not_recognized = models.TextField(
        default=('I\'m sorry, you can ask me things like...'))
    recommended_queries_statement = models.TextField(
        default=('I\'m sorry, did you wish to mean')
    )
    entry_not_present_in_database = models.TextField(
        default=('Sorry, we could not find the corresponding entry in the records.')
    )
    cancel_button_message = models.TextField(
        default='Hello, what would you like to know about?',
    )
    custom_stop_word = models.TextField(
        default='',
    )
    email_id = models.TextField(
        default='aman@allincall.in',
    )
    initial_message = models.TextField(
        default='Hi, I am AllinCall Virtual Assistant.',
    )
    base_response_1 = models.TextField(
        default='Hi',
        null=True,
        blank=True,
    )
    base_response_2 = models.TextField(
        default='',
        null=True,
        blank=True,
    )
    base_response_3 = models.TextField(
        default='',
        null=True,
        blank=True,
    )
    base_response_4 = models.TextField(
        default='',
        null=True,
        blank=True,
    )
    base_response_5 = models.TextField(
        default='',
        null=True,
        blank=True,
    )

    entities_enabled = models.BooleanField(default=False)
    intents_enabled = models.BooleanField(default=False)
    entities_group_enabled = models.BooleanField(default=False)
    question_entities_group_enabled = models.BooleanField(default=False)
    trees_enabled = models.BooleanField(default=False)
    word_mappers_enabled = models.BooleanField(default=False)
    mappers_enabled = models.BooleanField(default=False)
    sentences_enabled = models.BooleanField(default=False)
    auto_correct_words_enabled = models.BooleanField(default=False)
    channel_sentences_enabled = models.BooleanField(default=False)
    profile_enabled = models.BooleanField(default=False)
    query_cnt_enabled = models.BooleanField(default=False)
    variables_enabled = models.BooleanField(default=False)
    feedback_general_enabled = models.BooleanField(default=False)
    query_enabled = models.BooleanField(default=False)
    analytics_cnt_enabled = models.BooleanField(default=False)
    data_enabled = models.BooleanField(default=False)
    recommendations_enabled = models.BooleanField(default=False)
    feedback_query_enabled = models.BooleanField(default=False)
    config_enabled = models.BooleanField(default=False)
    unique_users_enabled = models.BooleanField(default=False)
    data_validators_enabled = models.BooleanField(default=False)
    file_storage = models.BooleanField(default=False)
    number_mappers_enabled = models.BooleanField(default=False)
    channel_enabled = models.BooleanField(default=False)
    language_enabled = models.BooleanField(default=False)
    leads_enabled = models.BooleanField(default=False)
    product_model_enabled = models.BooleanField(default=False)
    faq_enabled = models.BooleanField(default=False)
    testbot_chat_enabled = models.BooleanField(default=False)    
    
    url_customer_id = models.TextField(null=True,
                                       blank=True)
    url_show_policy = models.TextField(null=True,
                                       blank=True)
    parse_api_error_message = models.TextField(null=True,
                                               blank=True)
    encrypt = models.BooleanField(default=False)
    
    facebook_endpoint_url = models.TextField(null=True,
                                            blank=True)
    signals_enabled = models.BooleanField(default=True)

    prod = models.BooleanField(default=False)
    def __str__(self):
        return 'Config'


class Entities(models.Model):
    entity_name = models.TextField(blank=False,
                                   null=False)

    keywords = models.TextField(default='',
                                blank=True,
                                null=False,
                                help_text=("The keywords sets should be "
                                           "comma separated and the keywords "

                                           "should be space separated"))
    parent = models.ForeignKey("self",
                               null=True,
                               blank=True,
                               on_delete=models.CASCADE)

    level =  models.IntegerField(default=0)
    def __str__(self):
        return self.entity_name

    def get_keywords(self):
        keywords = list()
        keyword_sets = self.keywords.lower().split(',')

        for keyword_set in keyword_sets:
            keywords.append([keyword.strip()
                             for keyword in keyword_set.split(' ')])

        return keywords

    def is_this_entity(self, sentence):
        words = sentence.split()
        keyword_sets = self.get_keywords()

        for keyword_set in keyword_sets:

            keyword_set_present = True
            for keyword in keyword_set:
                if not keyword in words:
                    keyword_set_present = False
                    break
            if keyword_set_present:
                return True
        return False

    class Meta:
        verbose_name = 'Entity'
        verbose_name_plural = 'Entities'


class DataValidators(models.Model):
    function = models.TextField(default='',
                                null=True,
                                blank=True)

    entity_group = models.ForeignKey('EntityGroup',
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel,
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE)    
    run_at_start = models.BooleanField(default=False)
    def __str__(self):
        return self.function

    class Meta:
        verbose_name = 'Data Validators'
        verbose_name_plural = 'Data Validators'


class Data(models.Model):
    entity_name = models.TextField(
                                   null=False,
                                   blank=False)

    entity_value = models.TextField(
                                    null=False,
                                    blank=False)

    user = models.ForeignKey('Profile',
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)

    count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Data'
        verbose_name_plural = 'Data'

    def __str__(self):
        return self.entity_name + " " + self.entity_value


class Recommendation(models.Model):
    query = models.TextField(
                             null=False,
                             blank=False)
    entity = models.ForeignKey('Entities',
                               on_delete=models.CASCADE)
    intent = models.ForeignKey('Intent',
                               on_delete=models.CASCADE)

    def __str__(self):
        return self.query

    class Meta:
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'


class Files(models.Model):
    file_name = models.TextField(
                                 null=True,
                                 blank=True)

    file = models.FileField(upload_to='files/')

    def __str__(self):
        return self.file_name

    class Meta:
        verbose_name = 'file - Files'
        verbose_name_plural = 'file - Files'


class QuestionsEntityGroup(models.Model):
    name = models.TextField(null=True,
                            blank=True)
    entity_group = models.ForeignKey('EntityGroup',
                                     on_delete=models.CASCADE)
    question = models.ForeignKey(ChannelSentences,
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE,
                                 related_name='question_entitytype',
                                 help_text='This is the question to be asked in the flow.')
    re_question = models.ForeignKey(ChannelSentences,
                                    blank=True,
                                    null=True,
                                    on_delete=models.CASCADE,
                                    related_name='re_question_entitytype',
                                    help_text='This is the question to be asked when user enters an invalid query.')
    class Meta:
        verbose_name = 'QuestionEntityGroup'
        verbose_name_plural = 'QuestionEntityGroup'

    def __str__(self):
        return self.name

class ApiMapper(models.Model):
    user_id = models.TextField(null=True,
                               blank=True)

    number = models.TextField(null=True,
                               blank=True)

    choice_name = models.TextField(null=True,
                                   blank=True)

class EntityGroup(models.Model):
    name = models.TextField(
                            null=False,
                            blank=False)

    choices = models.ManyToManyField(Entities,
                                     blank=True,
                                     related_name="entity_choices")

    is_clickable = models.BooleanField(default=True)
    is_typable = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    is_persistent = models.BooleanField(default=False)
    is_loop = models.BooleanField(default=False)
    multi = models.BooleanField(default=False)
    is_date = models.BooleanField(default=False)
    is_checkbox = models.BooleanField(default=False)
    is_typable_special = models.BooleanField(default=False)        
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'EntityGroup'
        verbose_name_plural = 'EntityGroup'


class Tree(models.Model):
    name = models.TextField(null=True,
                            blank=True)
    question_entity_type = models.ForeignKey(QuestionsEntityGroup,
                                             blank=True,
                                             null=True,
                                             on_delete=models.CASCADE)
    answer = models.ForeignKey(ChannelSentences,
                               blank=True,
                               null=True,
                               related_name='tree_answer',
                               on_delete=models.CASCADE)
    mapper = models.ManyToManyField('Mapper',
                                    blank=True,
                                    related_name='mappers')
    number_mapper = models.ManyToManyField('NumberMappers',
                                           blank=True,
                                           related_name='number_mappers')
    is_diversify = models.BooleanField(default=False)
    is_tree_mapper_create = models.BooleanField(default=True)
    is_fixed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tree'
        verbose_name_plural = 'Tree'

class TestModel(models.Model):
    intent_id = models.TextField(blank=True,
                            null=True)
    name = models.TextField(blank=True,
                            null=True)

    sentences = models.TextField(blank=True,
                                 null=True)
    def __str__(self):
        return self.name

class Intent(models.Model):
    name = models.TextField(
                            null=False,
                            blank=False)
    keywords = models.TextField(default='',
                                blank=False,
                                null=False,
                                help_text=("The keywords sets should be "
                                           "comma separated and the keywords "
                                           "should be space separated"))
    restricted_keywords = models.TextField(default='',
                                           blank=True,
                                           null=True,
                                           help_text=("The keywords sets should be "
                                                      "comma separated and the keywords "
                                                      "should be space separated"))
    tree = models.ForeignKey(Tree,
                             null=True,
                             blank=True,
                             related_name="intent_set",
                             on_delete=models.CASCADE)
    answer = RichTextField(config_name='default',
                           null=True,
                           blank=True)
    level = models.IntegerField(default=1)
    test_sentences = models.TextField(default='',
                                      blank=True,
                                      null=True,
                                      help_text=("sentences should be separeted by new line."))
    misc = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_keywords(self):
        keywords = list()
        if not Config.objects.all()[0].encrypt:
            keyword_sets = decrypt(OFFSET,self.keywords).lower().split(',')
        else:
            keyword_sets = self.keywords.lower().split(",")

        for keyword_set in keyword_sets:
            keywords.append([keyword.strip()
                             for keyword in keyword_set.split(' ')])

        return keywords

    def get_bad_keywords(self):
        keywords = list()
        keyword_sets = self.restricted_keywords.lower().split(',')

        for keyword_set in keyword_sets:
            keywords.append([keyword.strip()
                             for keyword in keyword_set.split(' ')])

        return keywords

    def get_intent_score(self, sentence):
        words = sentence.split()
        keyword_sets = self.get_keywords()
        restricted_keyword_sets = self.get_bad_keywords()

        count_keyword_present = 0
        bool_restricted_keyword_present = False

        for keyword_set in keyword_sets:
            temp_count = 0
            for keyword in keyword_set:
                if keyword in words:
                    temp_count = temp_count + 1
            if temp_count > count_keyword_present:
                count_keyword_present = temp_count

        for keyword_set in restricted_keyword_sets:
            keyword_set_present = True
            for keyword in keyword_set:
                if not keyword in words:
                    keyword_set_present = False
                    break
            if keyword_set_present:
                bool_restricted_keyword_present = True

        if bool_restricted_keyword_present == False:
            return count_keyword_present
        return 0

    def is_this_intent(self, sentence):
        words = sentence.split()
        keyword_sets = self.get_keywords()
        restricted_keyword_sets = self.get_bad_keywords()

        bool_keyword_present = False
        bool_restricted_keyword_present = False

        for keyword_set in keyword_sets:
            keyword_set_present = True
            for keyword in keyword_set:
                if not keyword in words:
                    keyword_set_present = False
                    break
            if keyword_set_present:
                bool_keyword_present = True

        for keyword_set in restricted_keyword_sets:
            keyword_set_present = True
            for keyword in keyword_set:
                if not keyword in words:
                    keyword_set_present = False
                    break
            if keyword_set_present:
                bool_restricted_keyword_present = True

        if bool_keyword_present == True and bool_restricted_keyword_present == False:
            return True
        return False

    class Meta:
        verbose_name = 'Intent'
        verbose_name_plural = 'Intents'


class NumberMappers(models.Model):
    number = models.TextField(null=False,
                              blank=False)
    values = models.TextField(null=False,
                              blank=False)
    name = models.TextField(
                            null=True,
                            blank=True)

    def __str__(self):
        return self.name

class Mapper(models.Model):
    entity = models.ForeignKey(Entities,
                               on_delete=models.CASCADE,
                               null=True,
                               blank=True)
    next_tree = models.ForeignKey('Tree',
                                  null=True,
                                  blank=True,
                                  related_name='tree_mapper',
                                  on_delete=models.CASCADE)
    name = models.TextField(
                            null=True,
                            blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Mapper'
        verbose_name_plural = 'Mappers'


class QueryCnt(models.Model):
    query = models.TextField(
                             null=True,
                             blank=True)
    count = models.IntegerField(default=0)
    language = models.ForeignKey('Language',
                                 null=True,
                                 blank=True,
                                 on_delete=models.CASCADE)
    channel = models.ForeignKey('Channel',
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE)

    def __str__(self):
        return self.query


class UniqueUsers(models.Model):
    user_id = models.TextField(
                               null=False,
                               blank=False)

    time = models.DateField(auto_now=True)

    def __str__(self):
        return self.user_id


class Profile(models.Model):
    user_id = models.CharField(max_length=500,
                               null=True,
                               blank=False)
    tree = models.ForeignKey(Tree,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE)
    current_intent = models.ForeignKey(Intent,
                                       null=True,
                                       blank=True,
                                       on_delete=models.CASCADE)
    current_entity = models.ForeignKey(Entities,
                                       null=True,
                                       blank=True,
                                       on_delete=models.CASCADE)
    current_query = models.TextField(
                                     null=True,
                                     blank=True)
    re_question = models.BooleanField(default=False)
    stage = models.TextField(null=True,
                             blank=True,
                             default="pre")

    def __str__(self):
        return self.user_id

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profile'


class Log(models.Model):
    query = models.TextField(
                             null=True,
                             blank=True)
    time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(Profile,
                             related_name='Profile2',
                             on_delete=models.CASCADE)
    language = models.ForeignKey('Language',
                                 null=True,
                                 blank=True,
                                 on_delete=models.CASCADE)
    channel = models.ForeignKey('Channel',
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE)
    answer_succesfull = models.BooleanField(default=False)
    chatbot_answer = models.TextField(
                                      null=True,
                                      blank=True)
    clicked = models.BooleanField(default=False)

    def __str__(self):
        return self.query + str(self.time)

    class Meta:
        verbose_name = 'Log'
        verbose_name_plural = 'Logs'

class Leads(models.Model):
    name = models.TextField(null=True,
                            blank=True)
    email_id = models.TextField(null=True,
                            blank=True)
    contact = models.TextField(null=True,
                            blank=True)

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'

class WordMapper(models.Model):
    keyword = models.TextField(
                               default='',
                               null=True,
                               blank=True)

    similar_words = models.TextField(default='',
                                     blank=False,
                                     null=False)

    def get_similar_words(self):
        return [decrypt(OFFSET,word.strip()) for word in self.similar_words.split(',')]

    def __str__(self):
        return self.keyword

    class Meta:
        verbose_name = 'WordMapper'
        verbose_name_plural = 'WordMappers'

class BillApi(models.Model):
    file = models.FileField(upload_to='bill_files')    

class BillApiCustom(models.Model):
    payee_id = models.TextField(null=True,
                                blank=True)

    payee_name = models.TextField(null=True,
                                blank=True)

    payee_type = models.TextField(null=True,
                                blank=True)

def load_dictionary():
    words = set()
    WORD_MAP = {}
    word_mappers = WordMapper.objects.all()
    for word_mapper in word_mappers:
        for similar_word in word_mapper.get_similar_words():
            WORD_MAP[similar_word] = word_mapper.keyword

    for word in WORD_MAP:
        if word != '':
            words.add(word)
        if WORD_MAP[word] != '':
            words.add(WORD_MAP[word])

    intents = Intent.objects.all()
    for intent in intents:
        keywords = [item for sublist in intent.get_keywords()
                    for item in sublist]
        for keyword in keywords:
            if keyword != '':
                words.add(keyword)

    entities = Entities.objects.all()
    for entity in entities:
        keyword_sets = entity.get_keywords()
        for keyword_set in keyword_sets:
            for keyword in keyword_set:
                words.add(keyword)

    f = open(DICTIONARY_FILE, 'r+')
    f.truncate()

    for word in words:
        f.write(word.lower() + '\n')
    f.close()

def encrypt(n, plaintext):
    result = ''
    for l in plaintext.lower():
        try:
            i = (KEY.index(l) + n) % len(KEY)
            result += KEY[i]
        except ValueError:
            result += l
    return result.lower()

def decrypt(n, ciphertext):
    result = ''
    for l in ciphertext:
        try:
            i = (KEY.index(l) - n) % len(KEY)
            result += KEY[i]
        except ValueError:
            result += l
    return result.lower()

@receiver(pre_save, sender=Intent, dispatch_uid="update_entity_pre_count")
def update_entity_pre(sender, instance, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    try:
        if hasattr(instance, '_dirty'):
            del instance._dirty
            return
        if instance.id:
            old_instance = Intent.objects.get(pk=instance.id)
            list_1 = old_instance.keywords.split(",")
            list_2 = instance.keywords.split(",")
            decrypt_list = [item for item in list_1 if item in list_2]
            simple_add = [item for item in list_2 if item not in list_1]
            final_decrypted = [decrypt(OFFSET,item) for item in decrypt_list]
            simple_add = final_decrypted + simple_add
            final_encrypted = [encrypt(OFFSET,item) for item in simple_add]
            final_keywords = ','.join(final_encrypted)
            try:
                instance.keywords = final_keywords
                instance._dirty = True
                instance.save()
            finally:
                del instance._dirty
    except:
        pass

@receiver(pre_save, sender=WordMapper, dispatch_uid="update_wordmapper_pre_count")
def update_wordmapper_pre(sender, instance, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    try:
        if hasattr(instance, '_dirty'):
            del instance._dirty
            return
        if instance.id:
            old_instance = WordMapper.objects.get(pk=instance.id)
            list_1 = old_instance.similar_words.split(",")
            list_2 = instance.similar_words.split(",")
            decrypt_list = [item for item in list_1 if item in list_2]
            simple_add = [item for item in list_2 if item not in list_1]
            final_decrypted = [decrypt(OFFSET,item) for item in decrypt_list]
            simple_add = final_decrypted + simple_add
            final_encrypted = [encrypt(OFFSET,item) for item in simple_add]
            final_keywords = ','.join(final_encrypted)
            try:
                instance.similar_words = final_keywords
                instance._dirty = True
                instance.save()
            finally:
                del instance._dirty
    except:
        pass

@receiver(post_save, sender=BillApi, dispatch_uid="update_billapi_count")
def update_billapi(sender, instance, created, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return 
    print(instance.file)        
    csv.register_dialect('myDialect',
    delimiter = ',',
    quoting=csv.QUOTE_ALL,
    skipinitialspace=True)
    spamreader = csv.reader(instance.file, dialect='myDialect')
    for row in spamreader:
        print("ROW is: ", row)
        #row = row[0].split(",")        
        #row = row.split(",")
        try:
            BillApiCustom.objects.get(
                payee_id=row[0],
                payee_name=row[1],
                payee_type=row[2]
                )
        except:
            BillApiCustom(
                payee_id=row[0],
                payee_name=row[1],
                payee_type=row[2]
                ).save()

@receiver(post_save, sender=Variables, dispatch_uid="update_variable_count")
def update_variable(sender, instance, created, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return 
    if instance.variable_name != instance.variable_name.lower():
        instance.variable_name = instance.variable_name.lower()
        instance.save()


@receiver(post_save, sender=Entities, dispatch_uid="update_entity_count")
def update_entities(sender, instance, created, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    keywords = list()
    keyword_sets = instance.keywords.lower().split(',')

    for keyword_set in keyword_sets:
        keywords.append([keyword.strip()
                         for keyword in keyword_set.split(' ')])

    for word in keywords:
        for small_word in word:
            try:
                AutoCorrectWordList.objects.get(word=small_word)
            except:
                AutoCorrectWordList(word=small_word).save()


@receiver(post_save, sender=Intent, dispatch_uid="update_intent_count")
def update_intent(sender, instance, created, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    keywords = list()
    keyword_sets = instance.keywords.lower().split(',')

    for keyword_set in keyword_sets:
        keywords.append([keyword.strip()
                         for keyword in keyword_set.split(' ')])

    for word in keywords:
        for small_word in word:
            try:
                AutoCorrectWordList.objects.get(word=small_word)
            except:
                AutoCorrectWordList(word=small_word).save()

    if created == True and instance.answer is not None:
        x = instance.answer.replace(" ", "")
        if x != "":
            sentence = Sentences(sentence=instance.answer)
            sentence.language = Language.objects.get(name="eng")
            sentence.channel = Channel.objects.get(name="web")
            sentence.save()
            sentence = Sentences(sentence=instance.answer)
            sentence.language = Language.objects.get(name="eng")
            sentence.channel = Channel.objects.get(name="facebook")
            sentence.save()
            sentence = Sentences(sentence=instance.answer)
            sentence.language = Language.objects.get(name="eng")
            sentence.channel = Channel.objects.get(name="android")
            sentence.save()
            sentence = Sentences(sentence=instance.answer)
            sentence.language = Language.objects.get(name="eng")
            sentence.channel = Channel.objects.get(name="alexa")
            sentence.save()
            sentence = Sentences(sentence=instance.answer)
            sentence.language = Language.objects.get(name="eng")
            sentence.channel = Channel.objects.get(name="whatsapp")
            sentence.save()
            intent_name = instance.name
            tree_name = intent_name + INTENT_TREE_SUFFIX
            tree = Tree(name=tree_name)
            tree.save()
            tree.answer = ChannelSentences.objects.get(name=instance.answer)
            tree.save()
            instance.tree = tree
            instance.keywords = encrypt(OFFSET, instance.keywords)
            instance._dirty = True
            instance.save()
        else:
            intent_name = instance.name
            tree_name = intent_name + INTENT_TREE_SUFFIX
            tree = Tree(name=tree_name)
            tree.save()
            instance.tree = tree
            instance.keywords = encrypt(OFFSET, instance.keywords)
            instance._dirty = True
            instance.save()

def on_transaction_commit(func):
    def inner(*args, **kwargs):
        transaction.on_commit(lambda: func(*args, **kwargs))
    return inner

@receiver(post_save, sender=WordMapper, dispatch_uid="update_wm_count")
def update_wm(sender, instance, created, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    if created:
        instance.similar_words = encrypt(OFFSET, instance.similar_words)
        instance._dirty = True
        instance.save()

@receiver(post_save, sender=Log, dispatch_uid="update_log_count")
def update_log(sender, instance, created, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    if created:
        instance.query = encrypt(OFFSET, instance.query)
        instance.chatbot_answer = encrypt(OFFSET, instance.chatbot_answer)
        instance.save()

@receiver(post_save, sender=EntityGroup, dispatch_uid="update_entity_group_count")
def update_entity_group(sender, instance, created, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    if created and instance.is_typable:
        channels = Channel.objects.all()
        for channel in channels:
            DataValidators(channel=channel, entity_group=instance, function="def f(x):\r\n    return x").save()

@receiver(post_save, sender=Sentences, dispatch_uid="update_sentence_count")
def update_sentence(sender, instance, created, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    keywords = instance.sentence.lower().split(" ")
    for word in keywords:
        word = word.strip()
        word = word.replace("<p>","")
        word = word.replace("</p>", "")
        word = word.replace("&nbsp;", "")
        word = word.replace(".", "")
        try:
            AutoCorrectWordList.objects.get(word=word)
        except:
            AutoCorrectWordList(word=word).save()

@receiver(post_save, sender=Tree, dispatch_uid="update_tree_count")
@on_transaction_commit
def update_tree(sender, instance, **kwargs):
    if not Config.objects.all()[0].signals_enabled:
        return
    if instance.is_tree_mapper_create:
        if instance.question_entity_type:
            intent = instance.intent_set.all()
            intent_name = ""
            if intent.count() > 0:
                intent_name = intent[0].name
            else:
                intent_name = instance.name[:-5]

            entityType = instance.question_entity_type.entity_group
            choices = entityType.choices.all()
            str = intent_name + '.' + entityType.name + '.'

            list = []

            pass

            if (len(choices) == 0):
                treee = Tree.objects.filter(name=str + NULL_TREE_SUFFIX)
                if treee.count() == 0:
                    teee = Tree(name=str + NULL_TREE_SUFFIX)
                    teee.save()
            else:
                if instance.is_diversify:
                    for choice in choices:
                        list.append(choice.entity_name)
                        treee = Tree.objects.filter(name=str + list[0] + TREE_SUFFIX)
                        if treee.count() == 0:
                            teee = Tree(name=str + list[0] + TREE_SUFFIX)
                            teee.save()
                        list.pop()
                else:
                    treee = Tree.objects.filter(name=str + GENERAL + TREE_SUFFIX)
                    if treee.count() == 0:
                        pass
                        tee = Tree(name=str + GENERAL  + TREE_SUFFIX)
                        tee.save()

            mapper_list = []

            if (len(choices) == 0):
                tree = Tree.objects.filter(name=str + NULL_TREE_SUFFIX).get()
                try:
                    c = Entities.objects.get(entity_name=NULL)
                except:
                    c = Entities(entity_name=NULL,
                                 keywords=NULL)
                    c.save()

                mapy = Mapper(entity=c,
                              next_tree=tree,
                              name=str + NULL)
                mapy.save()
                mapper_list.append(mapy)
            else:
                if instance.is_diversify:
                    for choice in choices:
                        list.append(choice.entity_name)
                        tree = Tree.objects.filter(
                            name=str + list[0] + TREE_SUFFIX).get()
                        mapy = Mapper(entity=choice,
                                      next_tree=tree,
                                      name=str + list[0])
                        mapy.save()
                        mapper_list.append(mapy)
                        list.pop()
                else:
                    for choice in choices:
                        list.append(choice.entity_name)
                        tree = Tree.objects.filter(
                            name=str + GENERAL + TREE_SUFFIX).get()
                        mapy = Mapper(entity=choice,
                                      next_tree=tree,
                                      name=str + list[0])
                        mapy.save()
                        mapper_list.append(mapy)
                        list.pop()


            for mapp in mapper_list:
                instance.mapper.add(mapp)

