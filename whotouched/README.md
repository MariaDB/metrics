# Who Touched metrics

This is a tool to generate a list of who has committed in certain areas of code and how many times they have committed.

## Configuration

There is a file called `config.yaml` in the source, and this defines each area of code. There are three types of searches it can do to find each area of code, and combinations of these can be used together to define a single area of code.

As an example:

```yaml
Connect:
    paths: ["storage/connect"]
CMake:
    files_postfix: ["CMakeLists.txt"]
WIN32:
    define: "_WIN32"
    file_types: ["c", "cc", "h", "cpp", "hpp"]
```

The left aligned name is the name of the area of code, this will be used for the output CSV file name. The the types available are as follows:

### paths

The `paths` option provides a list of paths to search for commits in. Any commits to these paths count towards the count.

This is the quickest search mode.

### files_postfix

This option is a list of postfixes to find files across the codebase with. In the example case this is a full filename, but this would also match `MyCMakeLists.txt`. This is case sensitive and can be used for just file extensions such as `.c`.

This is slightly slower than `paths` but still quite quick.

### define

The `define` type looks in every file found in the code base that matches file extensions listed in `file_types`.

So, in the example given, it will look in all C / CPP and header files for `_WIN32` ifdefs and will mark commits in those areas of code as a contribution to this area. It is smart enough to handle nested ifdef blocks.

This is the slowest mode and can take around 45 minutes in the example given.

## Usage

To execute the tool you first need a git checkout of MariaDB Server somewhere, you can then execute with:

```sh
./whotouched.py /path/to/MariaDB/checkout
```

Possible extra options:

* `-v` - Verbose output
* `-d` - The oldest date of commit to include, in `YYYY-MM-DD` format
* `-o` - The CSV output directory, by default this is `output` in your working directory
