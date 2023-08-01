#/bin/bash

PYSIM_TRACE=../pySim-trace.py
GSMTAP_TRACE=pySim-trace_test_gsmtap.pcapng
TEMPFILE=temp.tmp

echo "pySim-trace_test - a test program to test pySim-trace.py"
echo "========================================================"

function usage {
    echo "Options:"
    echo "-o: generate .ok file"
}

function gen_ok_file {
    $PYSIM_TRACE gsmtap-pyshark-pcap -f $GSMTAP_TRACE > $GSMTAP_TRACE.ok
    echo "Generated file: $GSMTAP_TRACE.ok"
    echo "------------8<------------"
    cat $GSMTAP_TRACE.ok
    echo "------------8<------------"
}

function run_test {
    $PYSIM_TRACE gsmtap-pyshark-pcap -f $GSMTAP_TRACE | tee $TEMPFILE
    if [ ${PIPESTATUS[0]} -ne 0 ]; then
        echo ""
        echo "========================================================"
        echo "Testrun with $GSMTAP_TRACE failed (exception)."
        rm -f $TEMPFILE
        exit 1
    fi

    DIFF=`diff $GSMTAP_TRACE.ok $TEMPFILE`
    if ! [ -z "$DIFF" ]; then
        echo "Testrun with $GSMTAP_TRACE failed (unexpected output)."
        echo "------------8<------------"
        diff $GSMTAP_TRACE.ok $TEMPFILE
        echo "------------8<------------"
        rm -f $TEMPFILE
        exit 1
    fi

    echo ""
    echo "========================================================"
    echo "trace parsed without problems -- everything ok!"
    rm -f $TEMPFILE
}

OPT_GEN_OK_FILE=0
while getopts ":ho" OPT; do
    case $OPT in
        h)
            usage
            exit 0
            ;;
        o)
            OPT_GEN_OK_FILE=1
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
        ;;
    esac
done

if [ $OPT_GEN_OK_FILE -eq 1 ]; then
    gen_ok_file
    exit 0
else
    run_test
    exit 0
fi
