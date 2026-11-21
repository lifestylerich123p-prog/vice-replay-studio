"""Retention helpers: the per-second curve for Shorts and the biggest-drop finder (no network)."""
import statistics

from studio.retention import avg_med, curve_points, drop_summary, per_second


def line(points):
    """Sampled curve from (elapsed ratio, watch ratio) pairs, as YouTube returns it."""
    return sorted(points)


def test_per_second_reads_nearest_point_each_second():
    # a straight line from 100% at the start to 0% at the end, sampled every 1% of the video
    pts = line([(i / 100, 1 - i / 100) for i in range(101)])
    # length 4 s: seconds 0..4 map to ratios 0, .25, .5, .75, 1
    assert per_second(pts, 4.0) == [100, 75, 50, 25, 0]


def test_per_second_has_one_value_per_whole_second_plus_start():
    pts = line([(i / 100, 1 - i / 200) for i in range(101)])
    assert len(per_second(pts, 20.0)) == 21


def test_drop_summary_finds_largest_one_second_drop_and_never_uses_second_zero():
    secs = [100, 98, 95, 92, 90, 88, 40, 40]
    assert drop_summary(secs) == (6, 48)


def test_drop_summary_ignores_a_rise_at_second_zero():
    secs = [60, 90, 80, 70]  # the jump 60 -> 90 is a rise, not a drop
    second, loss = drop_summary(secs)
    assert second != 0 and loss >= 0


def test_curve_points_reads_hook_at_ten_percent_and_end_value():
    pts = line([(0.0, 1.0), (0.1, 0.8), (0.5, 0.6), (1.0, 0.4)])
    assert curve_points(pts) == (80, 40)


def test_avg_med_is_safe_on_empty_and_rounds_median():
    assert avg_med([]) == "-"
    assert avg_med([50, 60, 70]) == 60
    assert avg_med([10, 20]) == round(statistics.median([10, 20]))
