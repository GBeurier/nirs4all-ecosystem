# Public R product qualification; ecosystem owns these cross-repository recipes.
WORKSPACE_ROOT ?= $(N4A_WORKSPACE_ROOT)
ifeq ($(strip $(WORKSPACE_ROOT)),)
WORKSPACE_ROOT := $(abspath ..)
endif
CORE_ROOT := $(WORKSPACE_ROOT)/nirs4all-core
ECOSYSTEM_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
R_PARITY_LIB ?= $(CORE_ROOT)/.r-parity-lib
RSCRIPT ?= Rscript

.PHONY: test-r-parity
test-r-parity:
	mkdir -p "$(R_PARITY_LIB)"
	NIRS4ALL_E2E_R_LIB="$(R_PARITY_LIB)" $(RSCRIPT) "$(ECOSYSTEM_ROOT)/tests/runtime/r/install-public.R"
	cd "$(CORE_ROOT)" && R_LIBS_USER="$(R_PARITY_LIB):$${R_LIBS_USER:-}" NIRS4ALL_CORE_REQUIRE_METHODS_PARITY=1 NIRS4ALL_CORE_R_PARITY_LIB="$(R_PARITY_LIB)" NIRS4ALL_CORE_PARITY_ORACLE="$(CORE_ROOT)/tests/parity/expected/portable_python_oracle.json" NIRS4ALL_CORE_PARITY_FIXTURES="$(CORE_ROOT)/tests/parity/fixtures" $(RSCRIPT) "$(ECOSYSTEM_ROOT)/tests/runtime/r/parity.R"
