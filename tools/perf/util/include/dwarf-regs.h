#ifndef _PERF_DWARF_REGS_H_
#define _PERF_DWARF_REGS_H_

#include "generated/autoconf.h"

#ifdef CONFIG_LIBDWARF
const char *get_arch_regstr(unsigned int n);
#endif

#endif
