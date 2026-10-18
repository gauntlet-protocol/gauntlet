from completion.exup_bridge import bridge
from conformance.effect_boundary import evaluate as effect_evaluate
from completion.completion import evaluate as completion_evaluate

assert callable(bridge)
assert callable(effect_evaluate)
assert callable(completion_evaluate)
