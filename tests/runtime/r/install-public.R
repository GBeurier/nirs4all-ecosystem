lib <- Sys.getenv("NIRS4ALL_E2E_R_LIB")
stopifnot(nzchar(lib), dir.exists(lib))
.libPaths(c(lib, .libPaths()))
# Required CRAN Imports of the public nirs4all 0.7.2 tarball. Installing a
# tarball with repos = NULL does not resolve these dependencies automatically.
# n4m 1.3.4 additionally imports only stats; stats and tools ship with R.
required_cran <- c("digest", "jsonlite", "yaml")
available <- vapply(required_cran, requireNamespace, logical(1), quietly = TRUE)
if (any(!available)) {
  install.packages(required_cran[!available], lib = lib,
    repos = "https://cloud.r-project.org")
}
stopifnot(all(vapply(c(required_cran, "stats", "tools"),
  requireNamespace, logical(1), quietly = TRUE)))
expected <- c(n4m = "1.3.4", nirs4all = "0.7.2")
for (package in names(expected)) {
  description <- file.path(lib, package, "DESCRIPTION")
  installed <- file.exists(description) &&
    identical(as.character(packageVersion(package, lib.loc = lib)), expected[[package]])
  if (!installed) {
    if (package == "n4m") {
      install.packages(package, lib = lib,
        repos = c("https://gbeurier.r-universe.dev", "https://cloud.r-project.org"))
    } else {
      install.packages("https://github.com/GBeurier/nirs4all-r/releases/download/v0.7.2/nirs4all_0.7.2.tar.gz",
        lib = lib, repos = NULL, type = "source")
    }
  }
  stopifnot(identical(as.character(packageVersion(package, lib.loc = lib)), expected[[package]]))
  stopifnot(requireNamespace(package, quietly = TRUE))
}
