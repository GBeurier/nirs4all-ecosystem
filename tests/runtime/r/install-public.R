lib <- Sys.getenv("NIRS4ALL_E2E_R_LIB")
stopifnot(nzchar(lib), dir.exists(lib))
.libPaths(c(lib, .libPaths()))
expected <- c(n4m = "1.3.4", nirs4all = "0.7.1")
for (package in names(expected)) {
  description <- file.path(lib, package, "DESCRIPTION")
  installed <- file.exists(description) &&
    identical(as.character(packageVersion(package, lib.loc = lib)), expected[[package]])
  if (!installed) {
    if (package == "n4m") {
      install.packages(package, lib = lib,
        repos = c("https://gbeurier.r-universe.dev", "https://cloud.r-project.org"))
    } else {
      install.packages("https://github.com/GBeurier/nirs4all-r/releases/download/v0.7.1/nirs4all_0.7.1.tar.gz",
        lib = lib, repos = NULL, type = "source")
    }
  }
  stopifnot(identical(as.character(packageVersion(package, lib.loc = lib)), expected[[package]]))
}
