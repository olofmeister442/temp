from engine.models import *

print "Starting to delete various models"

UserPipe.objects.all().delete()
AnalyticCount.objects.all().delete()
QueryFeedbackCounter.objects.all().delete()
Variables.objects.all().delete()
Data.objects.all().delete()
Recommendation.objects.all().delete()
Files.objects.all().delete()
TestModel.objects.all().delete()
NumberMappers.objects.all().delete()
QueryCnt.objects.all().delete()
UniqueUsers.objects.all().delete()
Profile.objects.all().delete()
Leads.objects.all().delete()
WordMapper.objects.all().delete()

Sentences.objects.all().delete()
ChannelSentences.objects.all().delete()
Channel.objects.all().delete()
Language.objects.all().delete()

Entities.objects.all().delete()
EntityGroup.objects.all().delete()
QuestionsEntityGroup.objects.all().delete()

Intent.objects.all().delete()
Tree.objects.all().delete()

DataValidators.objects.all().delete()
Log.objects.all().delete()

AutoCorrectWordList.objects.all().delete()

print "Deleted various models"

print "Modifying Config to enable signals"
count = Config.objects.all().count()
if count == 0:
	Config().save()
config = Config.objects.all()[0]
config_current_signals_enabled = config.signals_enabled
config.signals_enabled = False
config.encrypt = True
config.save()

print "Creating Channel model"
Channel(name="web").save()

print "Creating Language model"
Language(name="eng").save()

print "Creating Sentences model"
sentence = Sentences(sentence="Hello", channel=Channel.objects.get(name="web"), language=Language.objects.get(name="eng"))
sentence.save()

print "Creating ChannelSentences model"
channel_sentences = ChannelSentences(name="Hello")
channel_sentences.save()
channel_sentences.group_of_sentences.add(sentence)

print "Creating Tree model"
tree = Tree(name="Hi.Tree", answer=channel_sentences)
tree.save()

print "Creating Intent model"
intent = Intent(name="Hi", keywords="hi,hello,hey", tree=Tree.objects.get(name="Hi.Tree"))
intent.save()

print "Creating AutoCorrect model"
word = AutoCorrectWordList(word="hi")
word.save()

print "Restoring Config"
config.signals_enabled = False
config.save()
