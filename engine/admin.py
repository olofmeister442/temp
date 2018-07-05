from django.contrib import admin
from django.contrib.auth.models import Group, User

from .constants import *
from .models import *
from .utils import get_entity, get_intent
from .views import do_pre_processing
from django.contrib.sessions.models import Session


class ConfigAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


class QuestionEntityGroupAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].question_entities_group_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class EntityGroupAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].entities_group_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class EntitiesAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'keywords', 'parent', )

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].entities_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class SentencesAdmin(admin.ModelAdmin):
    list_display = ('get_sentence', 'channel',)
    list_filter = ('channel',)
    list_per_page = LISTS_PER_PAGE

    def get_sentence(self, obj):
        return mark_safe(obj.sentence)

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].sentences_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class TreeAdmin(admin.ModelAdmin):
    list_display = ('name', 'question_entity_type', 'return_answer')
    list_filter = ('question_entity_type__entity_group__name',)
    list_per_page = LISTS_PER_PAGE

    def return_answer(self, obj):
        if obj.answer is not None:
            return obj.answer
        else:
            return ''

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].trees_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class QueryAdmin(admin.ModelAdmin):
    list_display = ('get_query', 'get_preprocessed_question', 'get_intent_question',
                    'get_entity_question', 'get_answer', 'answer_succesfull', 'clicked', 'time', 'channel')
    list_filter = ('time', 'answer_succesfull', 'clicked', )

    def get_query(self, obj):
        if not Config.objects.all()[0].encrypt:
            return decrypt(OFFSET, mark_safe(obj.query))
        else:
            return mark_safe(obj.query)

    def get_answer(self, obj):
        if not Config.objects.all()[0].encrypt:
            return decrypt(OFFSET, mark_safe(obj.chatbot_answer))
        else:
            return mark_safe(obj.chatbot_answer)

    def get_preprocessed_question(self, obj):
        try:
            if not Config.objects.all()[0].encrypt:
                return do_pre_processing(decrypt(OFFSET, obj.query), "web", "eng")
            else:
                return do_pre_processing(obj.query, "web", "eng")
        except:
            return obj.query

    def get_intent_question(self, obj):
        try:
            if not Config.objects.all()[0].encrypt:
                return get_intent(do_pre_processing(decrypt(OFFSET, obj.query), "web", "eng"))
            else:
                return get_intent(do_pre_processing(obj.query, "web", "eng"))
        except:
            return get_intent(do_pre_processing(obj.query, "web", "eng"))

    def get_entity_question(self, obj):
        try:
            if not Config.objects.all()[0].encrypt:
                return get_entity(do_pre_processing(decrypt(OFFSET, obj.query), "web", "eng"))
            else:
                return get_entity(do_pre_processing(obj.query, "web", "eng"))
        except:
            return get_entity(do_pre_processing(obj.query, "web", "eng"))

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].query_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class DataAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'entity_value', 'user')

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].data_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class IntentAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_keywords', 'get_bad', 'level', )
    list_per_page = LISTS_PER_PAGE

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].intents_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }

    def get_bad(self, obj):
        string = ', '.join(obj.restricted_keywords.split(','))
        return string

    def get_keywords(self, obj):
        string = ', '.join(obj.keywords.split(','))
        if Config.objects.all()[0].encrypt:
            return string
        else:
            return decrypt(OFFSET, string)


class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'faq_status', )
    list_filter = ('faq_status', )

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].faq_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class WordMapperAdmin(admin.ModelAdmin):
    list_display = ('get_keyword', 'get_similar_keyword', )

    def get_keyword(self, obj):
        return mark_safe(obj.keyword)

    def get_similar_keyword(self, obj):
        if not Config.objects.all()[0].encrypt:
            return decrypt(OFFSET, mark_safe(str(obj.similar_words)))
        else:
            return mark_safe(obj.similar_words)

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].word_mappers_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }

    def get_keywords(self, obj):
        return ', '.join(self.similar_words.split(','))


class ParentSentencesAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].channel_sentences_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class MapperAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].mappers_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class AutoCorrectWordListAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].auto_correct_words_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class ProfileAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].profile_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class QueryCntAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].query_cnt_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class VariablesAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].variables_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class AnalyticCountAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].analytics_cnt_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class RecommendationAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].recommendations_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class QueryFeedbackCounterAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].feedback_query_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class UniqueUsersAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].unique_users_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class DataValidatorsAdmin(admin.ModelAdmin):
    list_display = ('function', 'entity_group', 'channel')

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].data_validators_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class FilesAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].file_storage:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class LeadsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_id', 'contact',)

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].leads_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class ProductModelAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].product_model_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class LanguageAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].language_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class ChannelAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].channel_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class ApiCallsAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].apicalls_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class NumberMappersAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].number_mappers_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class TestModelAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True

    def get_model_perms(self, request):
        if not Config.objects.all()[0].testbot_chat_enabled:
            return {}
        else:
            return {
                'add': self.has_add_permission(request),
                'change': self.has_change_permission(request),
                'delete': self.has_delete_permission(request),
            }


class BillApiCustomAdmin(admin.ModelAdmin):
    list_display = ['payee_id', 'payee_name', 'payee_type']

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True


class VelocityChangesAdmin(admin.ModelAdmin):
    list_display = ['velocity_name', 'velocity_time',
                    'velocity_times', 'velocity_amount']

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True


class VelocityLogsAdmin(admin.ModelAdmin):
    list_display = ['velocity_id', 'mobile_number', 'time_created']

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return True


class SessionAdmin(admin.ModelAdmin):

    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']
admin.site.register(Session, SessionAdmin)
admin.site.register(Config, ConfigAdmin)
admin.site.register(QuestionsEntityGroup, QuestionEntityGroupAdmin)
admin.site.register(EntityGroup, EntityGroupAdmin)
admin.site.register(Entities, EntitiesAdmin)
admin.site.register(Sentences, SentencesAdmin)
admin.site.register(Tree, TreeAdmin)
admin.site.register(Log, QueryAdmin)
admin.site.register(Intent, IntentAdmin)
admin.site.register(WordMapper, WordMapperAdmin)
admin.site.register(ChannelSentences, ParentSentencesAdmin)
admin.site.register(Data, DataAdmin)

admin.site.register(Mapper, MapperAdmin)
admin.site.register(AutoCorrectWordList, AutoCorrectWordListAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(QueryCnt, QueryCntAdmin)
admin.site.register(Variables, VariablesAdmin)
admin.site.register(AnalyticCount, AnalyticCountAdmin)
admin.site.register(Recommendation, RecommendationAdmin)
admin.site.register(QueryFeedbackCounter, QueryFeedbackCounterAdmin)
admin.site.register(DataValidators, DataValidatorsAdmin)
admin.site.register(Files, FilesAdmin)
admin.site.register(Leads, LeadsAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(UniqueUsers, UniqueUsersAdmin)
admin.site.register(NumberMappers, NumberMappersAdmin)
admin.site.register(TestModel, TestModelAdmin)
admin.site.register(ApiMapper)
admin.site.register(BillApi)
admin.site.register(BillApiCustom, BillApiCustomAdmin)

admin.site.register(VelocityChanges, VelocityChangesAdmin)
admin.site.register(VelocityLogs, VelocityLogsAdmin)

admin.site.register(SysConfig)

admin.site.register(BusinessUser)
admin.site.register(ITUser)
admin.site.register(Logs_B)
admin.site.register(Logs_IT)
