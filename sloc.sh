#!/bin/sh

type und > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "SciTools Understand is not installed."
    exit 1
fi

usage=$(cat <<EOS
USAGE: $0 path database

Arguments

  path     : Absolute path to the directory containing the source code.
  database : Name of the SciTools Understand database.
EOS
)

if [ $# -lt 2 ]; then
    echo "$usage"
    exit 1
fi

path=$1
database=$2

cd $path

# Initialize

# Create an empty database
und create -languages c++ $database.udb

# Makes file paths RELATIVE:/foo.c. Simplifies replacing RELATIVE: with .
und settings -AddMode Relative $database.udb

# Add all files to the database. Understand decides the files to add depending
# on the "languages" setting the database has been created with.
und -db $database.udb add .

# Include the relative path of the file a function is declared in in metric
# report.
und settings -metricsShowDeclaredInFile on $database.udb
und settings -metricsFileNameDisplayMode RelativePath $database.udb
und settings -metricsDeclaredInFileDisplayMode RelativePath $database.udb

und settings -metricsWriteColumnTitles off $database.udb
und settings -metrics CountLineCode $database.udb

# Ignore preprocessor conditionals
und settings -C++IgnorePreprocessorConditionals on $database.udb

# Add additional include paths
und settings -c++includesadd $HOME/include/ $database.udb
und settings -c++includesadd /usr/include/linux $database.udb
und settings -c++includesadd /usr/include/sys $database.udb
und settings -c++includesadd /usr/include/c++/4.4.4/tr1/ $database.udb

# Analyze

und analyze $database.udb
und metrics $database.udb

# Post-process the metrics file to replace RELATIVE: with .
sed -i 's;RELATIVE:;.;g' $database.csv

# Clean-up
rm $database.udb
