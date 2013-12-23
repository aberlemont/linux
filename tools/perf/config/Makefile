uname_M := $(shell uname -m 2>/dev/null || echo not)

ARCH ?= $(shell echo $(uname_M) | sed -e s/i.86/i386/ -e s/sun4u/sparc64/ \
                                  -e s/arm.*/arm/ -e s/sa110/arm/ \
                                  -e s/s390x/s390/ -e s/parisc64/parisc/ \
                                  -e s/ppc.*/powerpc/ -e s/mips.*/mips/ \
                                  -e s/sh[234].*/sh/ -e s/aarch64.*/arm64/ )
CFLAGS := $(EXTRA_CFLAGS) $(EXTRA_WARNINGS)

# Additional ARCH settings for x86
ifeq ($(ARCH),i386)
  override ARCH := x86
  LIBUNWIND_LIBS = -lunwind -lunwind-x86
endif

ifeq ($(ARCH),x86_64)
  override ARCH := x86
  IS_X86_64 := 0
  ifeq (, $(findstring m32,$(CFLAGS)))
    IS_X86_64 := $(shell echo __x86_64__ | ${CC} -E -x c - | tail -n 1)
  endif
  ifeq (${IS_X86_64}, 1)
    RAW_ARCH := x86_64
    ARCH_INCLUDE = ../../arch/x86/lib/memcpy_64.S ../../arch/x86/lib/memset_64.S
    LIBUNWIND_LIBS = -lunwind -lunwind-x86_64
  else
    LIBUNWIND_LIBS = -lunwind -lunwind-x86
  endif
endif

ifeq ($(ARCH),arm)
  LIBUNWIND_LIBS = -lunwind -lunwind-arm
endif

ifeq ($(src-perf),)
src-perf := $(srctree)/tools/perf
endif

ifeq ($(obj-perf),)
obj-perf := $(OUTPUT)
endif

ifneq ($(obj-perf),)
obj-perf := $(abspath $(obj-perf))/
endif

LIB_INCLUDE := $(srctree)/tools/lib/

# include ARCH specific config
-include $(src-perf)/arch/$(ARCH)/Makefile

include $(src-perf)/config/utilities.mak

ifeq ($(call get-executable,$(FLEX)),)
  dummy := $(error Error: $(FLEX) is missing on this system, please install it)
endif

ifeq ($(call get-executable,$(BISON)),)
  dummy := $(error Error: $(BISON) is missing on this system, please install it)
endif

override PYTHON := \
  $(call get-executable-or-default,PYTHON,python)

override PYTHON_CONFIG := \
  $(call get-executable-or-default,PYTHON_CONFIG,$(PYTHON)-config)

# Treat warnings as errors unless directed not to
ifneq ($(WERROR),0)
  CFLAGS += -Werror
endif

ifndef DEBUG
  DEBUG := 0
endif

ifeq ($(DEBUG),0)
  CFLAGS += -O6
endif

ifdef PARSER_DEBUG
  PARSER_DEBUG_BISON := -t
  PARSER_DEBUG_FLEX  := -d
  CFLAGS             += -DPARSER_DEBUG
endif

CFLAGS += -fno-omit-frame-pointer
CFLAGS += -ggdb3
CFLAGS += -funwind-tables
CFLAGS += -Wall
CFLAGS += -Wextra
CFLAGS += -std=gnu99

EXTLIBS = -lpthread -lrt -lm -ldl

ifeq ($(CONFIG_CHECK_ENABLED),1)

ifneq ($(OUTPUT),)
  OUTPUT_FEATURES = $(OUTPUT)config/feature-checks/
  $(shell mkdir -p $(OUTPUT_FEATURES))
endif

feature_check = $(eval $(feature_check_code))
define feature_check_code
  feature-$(1) := $(shell $(MAKE) OUTPUT=$(OUTPUT_FEATURES) CFLAGS="$(EXTRA_CFLAGS)" LDFLAGS="$(LDFLAGS)" LIBUNWIND_LIBS="$(LIBUNWIND_LIBS)" PYTHON_CONFIG="$(PYTHON_CONFIG)" -C config/feature-checks test-$1 >/dev/null 2>/dev/null && echo 1 || echo 0)
endef

feature_set = $(eval $(feature_set_code))
define feature_set_code
  feature-$(1) := 1
endef

#
# Build the feature check binaries in parallel, ignore errors, ignore return value and suppress output:
#

#
# Note that this is not a complete list of all feature tests, just
# those that are typically built on a fully configured system.
#
# [ Feature tests not mentioned here have to be built explicitly in
#   the rule that uses them - an example for that is the 'bionic'
#   feature check. ]
#
CORE_FEATURE_TESTS =			\
	backtrace			\
	dwarf				\
	fortify-source			\
	glibc				\
	gtk2				\
	gtk2-infobar			\
	libaudit			\
	libbfd				\
	libelf				\
	libelf-getphdrnum		\
	libelf-mmap			\
	libnuma				\
	libperl				\
	libpython			\
	libpython-version		\
	libslang			\
	libunwind			\
	on-exit				\
	stackprotector			\
	stackprotector-all		\
	timerfd				\
	bionic				\
	liberty				\
	liberty-z			\
	cplus-demangle

#
# So here we detect whether test-all was rebuilt, to be able
# to skip the print-out of the long features list if the file
# existed before and after it was built:
#
ifeq ($(wildcard $(OUTPUT)config/feature-checks/test-all),)
  test-all-failed := 1
else
  test-all-failed := 0
endif

#
# Special fast-path for the 'all features are available' case:
#
$(call feature_check,all,$(MSG))

#
# Just in case the build freshly failed, make sure we print the
# feature matrix:
#
ifeq ($(feature-all), 0)
  test-all-failed := 1
endif

ifeq ($(test-all-failed),1)
  $(info )
  $(info Auto-detecting system features:)
endif

ifeq ($(feature-all), 1)
  #
  # test-all.c passed - just set all the core feature flags to 1:
  #
  $(foreach feat,$(CORE_FEATURE_TESTS),$(call feature_set,$(feat)))
else
  $(shell $(MAKE) OUTPUT=$(OUTPUT_FEATURES) CFLAGS="$(EXTRA_CFLAGS)" LDFLAGS=$(LDFLAGS) -i -j -C config/feature-checks $(CORE_FEATURE_TESTS) >/dev/null 2>&1)
  $(foreach feat,$(CORE_FEATURE_TESTS),$(call feature_check,$(feat)))
endif

#
# Print the result of the feature test:
#
feature_print = $(eval $(feature_print_code)) $(info $(MSG))

define feature_print_code
  ifeq ($(feature-$(1)), 1)
    MSG = $(shell printf '...%30s: [ \033[32mon\033[m  ]' $(1))
  else
    MSG = $(shell printf '...%30s: [ \033[31mOFF\033[m ]' $(1))
  endif
endef

#
# Only print out our features if we rebuilt the testcases or if a test failed:
#
ifeq ($(test-all-failed), 1)
  $(foreach feat,$(CORE_FEATURE_TESTS),$(call feature_print,$(feat)))
  $(info )
endif

else # !CONFIG_CHECK_ENABLED

-include include/config/auto.conf

endif # CONFIG_CHECK_ENABLED

ifeq ($(feature-stackprotector-all), 1)
  CFLAGS += -fstack-protector-all
endif

ifeq ($(feature-stackprotector), 1)
  CFLAGS += -Wstack-protector
endif

ifeq ($(DEBUG),0)
  ifeq ($(feature-fortify-source), 1)
    CFLAGS += -D_FORTIFY_SOURCE=2
  endif
endif

CFLAGS += -I$(src-perf)/include
CFLAGS += -I$(src-perf)/util/include
CFLAGS += -I$(src-perf)/arch/$(ARCH)/include
CFLAGS += -I$(srctree)/arch/$(ARCH)/include/uapi
CFLAGS += -I$(srctree)/arch/$(ARCH)/include
CFLAGS += -I$(srctree)/include/uapi
CFLAGS += -I$(srctree)/include

# $(obj-perf)      for generated common-cmds.h
# $(obj-perf)/util for generated bison/flex headers
ifneq ($(OUTPUT),)
CFLAGS += -I$(obj-perf)/util
CFLAGS += -I$(obj-perf)
endif

CFLAGS += -I$(src-perf)/util
CFLAGS += -I$(src-perf)
CFLAGS += -I$(LIB_INCLUDE)

CFLAGS += -D_LARGEFILE64_SOURCE -D_FILE_OFFSET_BITS=64 -D_GNU_SOURCE

ifdef CONFIG_BIONIC
  EXTLIBS := $(filter-out -lrt,$(EXTLIBS))
  EXTLIBS := $(filter-out -lpthread,$(EXTLIBS))
endif # CONFIG_BIONIC

ifdef CONFIG_LIBELF

  EXTLIBS += -lelf
  # TODO: to remove; already included above
  # include ARCH specific config
  -include $(src-perf)/arch/$(ARCH)/Makefile

  # libelf supported - what about dwarf?
  ifdef CONFIG_DWARF
    EXTLIBS += -ldw
  endif # CONFIG_DWARF

endif # CONFIG_LIBELF

ifdef CONFIG_LIBUNWIND
  EXTLIBS += $(LIBUNWIND_LIBS)
endif

ifdef CONFIG_LIBAUDIT
  EXTLIBS += -laudit
endif # CONFIG_LIBAUDIT

ifdef CONFIG_SLANG
  # Fedora has /usr/include/slang/slang.h, but ubuntu /usr/include/slang.h
  CFLAGS += -I/usr/include/slang
  EXTLIBS += -lslang
endif

ifdef CONFIG_GTK2
  GTK_CFLAGS += $(shell pkg-config --cflags gtk+-2.0 2>/dev/null)
  GTK_LIBS := $(shell pkg-config --libs gtk+-2.0 2>/dev/null)
  EXTLIBS += -ldl
endif

grep-libs  = $(filter -l%,$(1))
strip-libs = $(filter-out -l%,$(1))

ifdef CONFIG_LIBPERL
  PERL_EMBED_LDOPTS = $(shell perl -MExtUtils::Embed -e ldopts 2>/dev/null)
  PERL_EMBED_LDFLAGS = $(call strip-libs,$(PERL_EMBED_LDOPTS))
  PERL_EMBED_LIBADD = $(call grep-libs,$(PERL_EMBED_LDOPTS))
  PERL_EMBED_CCOPTS = `perl -MExtUtils::Embed -e ccopts 2>/dev/null`
  FLAGS_PERL_EMBED=$(PERL_EMBED_CCOPTS) $(PERL_EMBED_LDOPTS)
  LDFLAGS += $(PERL_EMBED_LDFLAGS)
  EXTLIBS += $(PERL_EMBED_LIBADD)
endif

ifdef CONFIG_LIBPYTHON
  PYTHON_CONFIG_SQ := $(call shell-sq,$(CONFIG_PYTHON_CONFIG_PATH))
  PYTHON_EMBED_LDOPTS := $(shell $(PYTHON_CONFIG_SQ) --ldflags 2>/dev/null)
  PYTHON_EMBED_LDFLAGS := $(call strip-libs,$(PYTHON_EMBED_LDOPTS))
  PYTHON_EMBED_LIBADD := $(call grep-libs,$(PYTHON_EMBED_LDOPTS))
  PYTHON_EMBED_CCOPTS := $(shell $(PYTHON_CONFIG_SQ) --cflags 2>/dev/null)
  FLAGS_PYTHON_EMBED := $(PYTHON_EMBED_CCOPTS) $(PYTHON_EMBED_LDOPTS)
  LDFLAGS += $(PYTHON_EMBED_LDFLAGS)
  EXTLIBS += $(PYTHON_EMBED_LIBADD)
  LANG_BINDINGS += $(obj-perf)python/perf.so
endif

ifdef CONFIG_DEMANGLE
  ifdef CONFIG_DEMANGLE_LIBBFD
    EXTLIBS += -lbfd
  endif
  ifdef CONFIG_DEMANGLE_LIBIBERTY
    EXTLIBS += -lbfd -liberty
  endif
  ifdef CONFIG_DEMANGLE_LIBIBERTY_Z
    EXTLIBS += -lbfd -liberty -lz
  endif
  ifdef CONFIG_CPLUS_DEMANGLE
    EXTLIBS += -lbfd
  endif
endif

ifdef CONFIG_LIBNUMA
  EXTLIBS += -lnuma
endif # CONFIG_LIBNUMA

# Among the variables below, these:
#   perfexecdir
#   template_dir
#   mandir
#   infodir
#   htmldir
#   ETC_PERFCONFIG (but not sysconfdir)
# can be specified as a relative path some/where/else;
# this is interpreted as relative to $(prefix) and "perf" at
# runtime figures out where they are based on the path to the executable.
# This can help installing the suite in a relocatable way.

# Makexb the path relative to DESTDIR, not to prefix
ifndef DESTDIR
prefix = $(HOME)
endif
bindir_relative = bin
bindir = $(prefix)/$(bindir_relative)
mandir = share/man
infodir = share/info
perfexecdir = libexec/perf-core
sharedir = $(prefix)/share
template_dir = share/perf-core/templates
htmldir = share/doc/perf-doc
ifeq ($(prefix),/usr)
sysconfdir = /etc
ETC_PERFCONFIG = $(sysconfdir)/perfconfig
else
sysconfdir = $(prefix)/etc
ETC_PERFCONFIG = etc/perfconfig
endif
ifeq ($(IS_X86_64),1)
lib = lib64
else
lib = lib
endif
libdir = $(prefix)/$(lib)

# Shell quote (do not use $(call) to accommodate ancient setups);
ETC_PERFCONFIG_SQ = $(subst ','\'',$(ETC_PERFCONFIG))
DESTDIR_SQ = $(subst ','\'',$(DESTDIR))
bindir_SQ = $(subst ','\'',$(bindir))
mandir_SQ = $(subst ','\'',$(mandir))
infodir_SQ = $(subst ','\'',$(infodir))
perfexecdir_SQ = $(subst ','\'',$(perfexecdir))
template_dir_SQ = $(subst ','\'',$(template_dir))
htmldir_SQ = $(subst ','\'',$(htmldir))
prefix_SQ = $(subst ','\'',$(prefix))
sysconfdir_SQ = $(subst ','\'',$(sysconfdir))
libdir_SQ = $(subst ','\'',$(libdir))

ifneq ($(filter /%,$(firstword $(perfexecdir))),)
perfexec_instdir = $(perfexecdir)
else
perfexec_instdir = $(prefix)/$(perfexecdir)
endif
perfexec_instdir_SQ = $(subst ','\'',$(perfexec_instdir))
