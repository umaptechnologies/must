from details.must_have_patterns import MustHavePatterns
from details.plastic import Plastic
from details.primitive_musts import must_be_string
from details.primitive_musts import must_be_natural_number
from details.primitive_musts import must_be_real_number
from details.primitive_musts import must_list_objects
from details.standard_patterns import MustOutputToStdOut

must_be_something = Plastic  # This is an alias for importing.
_ = (
    MustHavePatterns,
    must_be_string,
    must_be_natural_number,
    must_be_real_number,
    must_list_objects,
    MustOutputToStdOut,
)  # Just to get the linter to shut up
