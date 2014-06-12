import os
import sys
import itertools
import kconfiglib

# Let's set some environment variables to define the target
# architecture; we choose x86 because, so far, nearly all features are
# available on x86.
os.environ['ARCH'] = 'x86'
os.environ['IS_64_BIT'] = '1'
os.environ['CROSS_COMPILE'] = ''

# Load Kconfig pattern
ref_config = kconfiglib.Config(sys.argv[1])

# Generate defconfig (by default, all options are set to y)
ref_config.write_config('REF_config')

# Get all the symbols
symbols = dict([(s.get_name(), s) for s in ref_config.get_symbols()])

# Remove odd symbols
symbols.pop('y', None)
symbols.pop('m', None)
symbols.pop('n', None)

# Remove choice-related symbols
choices = ref_config.get_choices()
items = [c.get_items() for c in choices]
names = [i.get_name() for i in itertools.chain.from_iterable(items)]
for name in names:
    symbols.pop(name, None)

for name in symbols:
    symbol = symbols[name]
    if not symbol.is_modifiable():
        continue
    if symbol.get_value() != 'y':
        continue
    symbol.set_user_value('n')
    filename = 'NO_' + name + '_config'
    ref_config.write_config(filename)
    symbol.set_user_value('y')
