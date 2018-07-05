from engine.models import *

import json

f = open('engine.json').readlines()[0]
json_dict = json.loads(f)
print (len(json_dict))

# Creating channel
for model in json_dict:
   if model['model'] == 'engine.channel':
       pk = model["pk"]
       name = model["fields"]["name"]
       Channel(pk=pk, name=name).save()

for model in json_dict:
   if model['model'] == 'engine.language':
       pk = model["pk"]
       name = model["fields"]["name"]
       Language(pk=pk, name=name).save()

cnt = 0
for model in json_dict:
   if model['model'] == 'engine.wordmapper':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       keyword = model["fields"]["keyword"]
       similar_words = model["fields"]["similar_words"]
       WordMapper(pk=pk, keyword=keyword, similar_words=similar_words).save()


cnt = 0

for model in json_dict: 
   if model['model'] == 'engine.autocorrectwordlist':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       word = model["fields"]["word"]       
       AutoCorrectWordList(pk=pk, word=word).save()

cnt = 0
# Generating Sentences Now
print("Generating Sentences")
for model in json_dict:
   if model['model'] == 'engine.sentences':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       sentence = model["fields"]["sentence"]
       language = model["fields"]["language"]
       channel = model["fields"]["channel"]       
       lan = Language.objects.get(pk=language)
       chan = Channel.objects.get(pk=channel)
       Sentences(pk=pk, sentence=sentence, language=lan, channel=chan).save()
print("Exiting Sentences")

# Generating Channel Sentences Now  
cnt = 0
print("Generating ChannelSentences")
for model in json_dict:
   if model['model'] == 'engine.channelsentences':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       name = model["fields"]["name"]
       temp = ChannelSentences(pk=pk, name=name)
       temp.save()
       group_of_senten = model["fields"]["group_of_sentences"]
       for val in group_of_senten:
           temp.group_of_sentences.add(val)
           temp.save()
print("Exiting ChannelSentences")          


# Generating Entities Now
cnt = 0
print("Generating Entities")
for model in json_dict:
    if model['model'] == 'engine.entities':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       entity_name = model["fields"]["entity_name"]    
       keywords = model["fields"]["keywords"]       
       Entities(pk=pk, entity_name=entity_name, keywords=keywords).save()
print("Exiting Entities")

cnt = 0
# Generating EntityGroup Now
print("Generating EntityGroup")
for model in json_dict:
   if model['model'] == 'engine.entitygroup':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       name = model["fields"]["name"]    
       is_clickable = model["fields"]["is_clickable"]    
       is_typable = model["fields"]["is_typable"]    
       is_primary = model["fields"]["is_primary"]    
       is_persistent = model["fields"]["is_persistent"]
       is_loop = model["fields"]["is_loop"]

       temp = EntityGroup(pk=pk, name=name, is_clickable=is_clickable, is_typable=is_typable, is_primary=is_primary,is_persistent=is_persistent,is_loop=is_loop)
       temp.save()
       choices_list = model["fields"]["choices"]
       for choice in choices_list:
           temp.choices.add(choice)
           temp.save()       
print("Exiting EntityGroup")

print("Generating QuestionEntityGroup")
cnt = 0
# Generating QuestionEntityGroup Now
for model in json_dict:
   if model['model'] == 'engine.questionsentitygroup':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       name = model["fields"]["name"]    
       entitygroup_id = model["fields"]["entity_group"]
       question_id = model["fields"]["question"]
       entity_group = EntityGroup.objects.get(pk=entitygroup_id)
       question = ChannelSentences.objects.get(pk=question_id)
       QuestionsEntityGroup(pk=pk, name=name, entity_group=entity_group, question=question).save()
print("Exiting QuestionsEntityGroup")

cnt = 0
for model in json_dict:
   if model['model'] == 'engine.tree':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]       
       Tree(pk=pk).save()

cnt = 0
for model in json_dict:
   if model['model'] == 'engine.intent':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       name = model["fields"]["name"]
       keywords = model["fields"]["keywords"]
       restricted_keywords = model["fields"]["restricted_keywords"]      
       test_sentences = model["fields"]["test_sentences"]
       misc = model["fields"]["misc"]
       level = model["fields"]["level"]

       tree_id = model["fields"]["tree"]
       a = Tree.objects.get(pk=tree_id)       
       Intent(pk=pk, name=name, level=level, keywords=keywords, restricted_keywords=restricted_keywords, test_sentences=test_sentences,misc=misc,tree=a).save()

#-----------------------------------------------------------------
cnt = 0
for model in json_dict:
   if model['model'] == 'engine.mapper':
       cnt = cnt + 1
       print("Processing: ", cnt)
       pk = model["pk"]
       name = model["fields"]["name"]
       entity_id = model["fields"]["entity"]
       tree_id = model["fields"]["next_tree"]
       Mapper(pk=pk, entity=Entities.objects.get(pk=entity_id), next_tree=Tree.objects.get(pk=tree_id), name=name).save()

cnt = 0
for model in json_dict:
   if model['model'] == 'engine.tree':
        try:
            cnt = cnt + 1
            print("Processing: ", cnt)
            pk = model["pk"]
            a = Tree.objects.get(pk=pk)
            a.name = model["fields"]["name"]
            if(model["fields"]["question_entity_type"]):
                a.question_entity_type = QuestionsEntityGroup.objects.get(pk=model["fields"]["question_entity_type"])       
            if(model["fields"]["answer"]):
                a.answer = ChannelSentences.objects.get(pk=model["fields"]["answer"])       
            a.is_diversify = model["fields"]["is_diversify"]
            a.is_tree_mapper_create = model["fields"]["is_tree_mapper_create"]
            a.is_fixed = model["fields"]["is_fixed"]
            a.save()
            mappers = model["fields"]["mapper"]
            for mapp in mappers:
                a.mapper.add(mapp)
                a.save()
        except Exception as e:
            print(str(e))


####################3
# Data Validators
cnt = 0

for model in json_dict:
   if model['model'] == 'engine.datavalidators':
        try:
            cnt = cnt + 1
            print("Processing: ", cnt)
            pk = model["pk"]
            function = model["fields"]["function"]
            entity_type_id = model["fields"]["entity_type"]
            DataValidators(function=function,entity_type=EntityGroup.objects.get(pk=entity_type_id)).save()
        except Exception as e:
            print(str(e))

