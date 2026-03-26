import math
from hypothesis import given, assume
from hypothesis import strategies as st


def moving_avg_sensor(values, window):
    if window <= 0 or window > len(values):
        return []
    out = []
    for i in range(0, len(values) - window + 1):
        seg = values[i:i + window]
        if seg.count(0) == 1:
            out.append(float("nan"))
        else:
            out.append(sum(seg) / window)
    return out


@given(
    values=st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=20),
    window=st.integers(min_value=1, max_value=20)
)
def test_property(values, window):
    assume(1 <= window <= len(values))

    result = moving_avg_sensor(values, window)

    for val in result:
        assert math.isfinite(val), (
            f"Got non-finite value {val} for values={values}, window={window}"
        )
