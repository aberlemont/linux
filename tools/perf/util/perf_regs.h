#ifndef __PERF_REGS_H
#define __PERF_REGS_H

#include <linux/kconfig.h>

#ifdef CONFIG_PERF_REGS
#include <perf_regs.h>
#else
#define PERF_REGS_MASK	0

static inline const char *perf_reg_name(int id __maybe_unused)
{
	return NULL;
}
#endif /* HAVE_PERF_REGS_SUPPORT */
#endif /* __PERF_REGS_H */
