from patterns import patterns
from plastic import Plastic


def test_duck():
    being1_location = patterns.create(Plastic().that_must_use(x=1,y=1))
    being1 = patterns.create(Plastic()
                             .that_must('start_conversation', returning='words')
                             .and_must_use(location=being1_location))

    being2_location = patterns.create(Plastic().that_must_use(x=0,y=0))
    being2 = patterns.create(Plastic()
                             .that_must('respond', 'words, source')
                             .must_use(location=being2_location)
                             .and_must_have('energy'))

    words = being1.start_conversation()
    being2.respond(words, being1)

    assert being2.energy == 82, being2.energy
    assert being2.location.x == -10 and being2.location.y == -10, being2.location

    print being2.energy
    print being2.location

if __name__ == "__main__":
    test_duck()
