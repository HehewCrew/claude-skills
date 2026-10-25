"""Cost of a print from the slicer's grams and time, and what a price earns per printer hour.

    python cost.py --grams 346 --hours 8.78 --filament 80 --kwh 0.35 --kw 0.12 \
        --rate 15 --reserve 3 --price 79 [--real-time 1.5 --real-grams 1.55]

--filament   price of 1 kg of filament (any currency; use the same one throughout)
--kwh, --kw  electricity price and the printer's average draw (a P1S on PLA is roughly 0.10-0.15 kW;
             measure with a plug meter; never use the PSU rating, which overstates it several times)
--rate       the machine-hour bar: price floor = material + electricity + rate x hours
--reserve    money set aside per paid hour (e.g. towards a second printer); reported as a share
--price      a selling price to check: what it earns per printer hour after plastic and electricity
--real-*     factors when the owner's real prints run heavier/slower than the slicer (compare one real plate)
"""
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--grams", type=float, required=True)
ap.add_argument("--hours", type=float, required=True)
ap.add_argument("--filament", type=float, required=True)
ap.add_argument("--kwh", type=float, default=0.0)
ap.add_argument("--kw", type=float, default=0.12)
ap.add_argument("--rate", type=float, default=0.0)
ap.add_argument("--reserve", type=float, default=0.0)
ap.add_argument("--price", type=float)
ap.add_argument("--min-markup", type=float, default=3.0)
ap.add_argument("--real-time", type=float, default=1.0)
ap.add_argument("--real-grams", type=float, default=1.0)
a = ap.parse_args()

g, h = a.grams * a.real_grams, a.hours * a.real_time
mat, elec = g * a.filament / 1000, h * a.kw * a.kwh
cost = mat + elec
print(f"{g:.0f} g, {h:.2f} h -> filament {mat:.2f} + electricity {elec:.2f} = cost {cost:.2f}")
print(f"floor at {a.min_markup:g}x cost: {a.min_markup * cost:.2f}")
if a.rate:
    print(f"floor at {a.rate:g}/machine-hour: {cost + a.rate * h:.2f}")
if a.price:
    per_h = (a.price - cost) / h
    print(f"at {a.price:g}: earns {per_h:.2f} per printer hour after plastic and electricity", end="")
    print(f"; the {a.reserve:g}/h reserve takes {a.reserve / per_h:.0%} of it" if a.reserve and per_h > 0 else "")
