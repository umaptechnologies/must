from patterns import patterns
from must import new_thing

being1_location = patterns.create(new_thing().that_must_use(x=1,y=1))
being1 = patterns.create(new_thing()
                         .that_must('start_conversation', returning='words')
                         .and_must_use(location=being1_location))

being2_location = patterns.create(new_thing().that_must_use(x=0,y=0))
being2 = patterns.create(new_thing()
                         .that_must('respond', 'words, source')
                         .must_use(location=being2_location)
                         .and_must_have('energy'))

words = being1.start_conversation()
being2.respond(words, being1)
print being2.energy
print being2.location
