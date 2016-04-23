from patterns import patterns
from Vector2D import Vector2D

conversation_starter = patterns.create(lambda thing: thing.that_must('start_conversation', '', 'words').and_must_use(location=Vector2D(1,1)))
being = patterns.create(lambda thing: thing.that_must('respond', 'words, source', '').must_use(location=Vector2D(0,0)).and_must_have('energy'))

words = conversation_starter.start_conversation()
being.respond(words, conversation_starter)
print being.energy
