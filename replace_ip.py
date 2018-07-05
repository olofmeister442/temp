from engine.models import *

prev_ip = "172.16.18.249:443"
new_ip = "127.0.0.1:8000"

for s in Sentences.objects.all():
	s.sentence = s.sentence.replace(prev_ip, new_ip)
	s.save()

for valid in DataValidators.objects.all():
	valid.function = valid.function.replace(prev_ip, new_ip)
	valid.save()

