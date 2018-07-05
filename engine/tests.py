import uuid

from django.test import TestCase
from .models import *
from .utils import *
# Create your tests here.

class SimpleTestCase(TestCase):

    def setUp(self):
        Config(signals_enabled=True, encrypt=True).save()

        Channel(name="web").save()
        Language(name="eng").save()

        sentence = Sentences(sentence="Hello", channel=Channel.objects.get(name="web"), language=Language.objects.get(name="eng"))
        sentence.save()

        channel_sentences = ChannelSentences(name="Hello")
        channel_sentences.save()
        channel_sentences.group_of_sentences.add(sentence)

        tree = Tree(name="Hi.Tree", answer=channel_sentences)
        tree.save()

        intent = Intent(name="Hi", keywords="hi,hello,hey", tree=Tree.objects.get(name="Hi.Tree"))
        intent.save()

    def test_chat(self):
        intent_list = get_intent("Hi")

        self.assertEqual(len(intent_list), 1)
        self.assertEqual(intent_list[0].name, "Hi")

        intent_list = get_intent("random")

        self.assertEqual(intent_list, None)
        print("Passed: SimpleTestCase, test_chat")

def create_channel_sentence(text):
    sentence = Sentences(sentence=text, channel=Channel.objects.get(name="web"), language=Language.objects.get(name="eng"))
    sentence.save()

    channel_sentence = ChannelSentences(name=text)
    channel_sentence.save()
    channel_sentence.group_of_sentences.add(sentence)

    return channel_sentence

class TypableEntityTestCase(TestCase):

    def setUp(self):
        Config(signals_enabled=False, encrypt=True).save()

        Channel(name="web").save()
        Language(name="eng").save()

        channel_sentence_1 = create_channel_sentence("Hello, whats your mobile number")
        channel_sentence_2 = create_channel_sentence("You spoke {/ MobileNumber /}")

        mobile_number = EntityGroup(name="MobileNumber", is_typable=True, is_clickable=False)
        mobile_number.save()

        question_entity_group = QuestionsEntityGroup(name="MobileNumber", entity_group=mobile_number, question=channel_sentence_1)
        question_entity_group.save()

        entity = Entities(entity_name="null", keywords="null")
        entity.save()

        tree = Tree(name="Hi.Tree", question_entity_type=question_entity_group)
        tree.save()

        next_tree = Tree(name="Hi.Tree.null")
        next_tree.save()

        mapper = Mapper(name="Hi.Tree", entity=entity, next_tree=next_tree)
        mapper.save()

        tree.mapper.add(mapper)
        tree.save()

        next_tree.answer = channel_sentence_2
        next_tree.save()

        intent = Intent(name="Hi", keywords="hi,hello,hey", tree=Tree.objects.get(name="Hi.Tree"))
        intent.save()

        print(Intent.objects.all())
        print(Tree.objects.all())
        print(Mapper.objects.all())
        print(Tree.objects.all()[0].name, Tree.objects.all()[0].mapper.all())

    def test_chat(self):
#        intent_list = get_intent("Hi")
#
#        self.assertEqual(len(intent_list), 1)
#        self.assertEqual(intent_list[0].name, "Hi")
#
#        intent_list = get_intent("random")
#
#        self.assertEqual(intent_list, None)
        user_id = str(uuid.uuid4())
        user = Profile(user_id=user_id)
        user.save()

        response = process_message_without_pipe(None, "Hi", user_id, "web", "eng", "1", "")
        self.assertEqual(response["response"].strip(), "Hello, whats your mobile number")
        print(user.tree)
        response = process_message_without_pipe(user.tree, "9033988878", user_id, "web", "eng", "1", "")
        print(response)

