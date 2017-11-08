<!DOCTYPE html>


<%!
    def createTests(ec_seq, ec_info):
      """
      Creates the graphic output for all tests.
      :param ec_seq: Entity category sequence as a list." \
      :param ec_info: Entity category dictionary with.
      :return: A graphic element for each category.
      """
      element = ""
      for ec in ec_seq:
        name = ec
        desc = ""
        if ec in ec_info:
            name = ec_info[ec]["Name"]
            desc = ec_info[ec]["Description"]

        if ec == "":
            ec = "base"
        element += '<div id="' + ec + '" name="' + name + '" status="4" class="row extrarow" ' \
                   'onmouseover="showHoverColor(\'' + ec + '\');" onmouseout="showOriginalColor(\'' + ec + '\');">'
        element += '    <div class="col-md-7" onclick="toggleDisplay(\'' + ec + '_extra\');' \
        '                   toggleArrow(\'' + ec + '_arrow\',\'static/arrowRight.png\',\'static/arrowDown.png\');">' \
                            '<img id="' + ec + '_arrow" src="static/arrowRight.png" />' \
                            '&nbsp;' + name + '</div>'
        element += '    <div id="' + ec + '_status" class="col-md-3">Not run</div><div class="col-md-2">'
        element += '        <div class="btn btn-sm btn-primary" onclick="runTest(\'' + ec + '\')">Run test</div>'
        element += '    </div>'
        element += '    <div id="' + ec + '_extra" class="extra"><div class="inner_extra">'
        element += '        <div id="' + ec + '_result" class="result"><div class="textleft"><b>Test result</b><br />No result exists.</div></div>'
        element += '        <div id="' + ec + '_info" class="information"><div class="textright">' + desc +'</div></div>'
        element += '    </div></div>'
        element += '</div>'

      return element
%>

<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" type="text/css" href="static/style.css" media="all"/>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css" integrity="sha384-PsH8R72JQ3SOdhVi3uxftmaW6Vc51MKb0q5P2rRUpPvrszuE4W1povHYgTpBfshb" crossorigin="anonymous">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <script src="static/jquery.min.1.9.1.js"></script>
    <script src="static/jquery.tinysort.charorder.min.js"></script>
    <script src="static/jquery.tinysort.min.js"></script>


    <title></title>
    <script language="JavaScript">
        var $j = jQuery.noConflict();

        var sortByNameValue = 1;
        var sortByStatusValue = 2;

        var testRunning = -1;
        var tests = new Array();
        var testIsRunning = false;

        var ec_seq = ${ec_seq};
        var sortOrder=sortByNameValue;
        var isLoggedIn = false;

        function toggleArrow(id,pic1,pic2) {
            if ($j('#'+id).attr('src') === pic1) {
                $j('#'+id).attr('src',pic2);
            } else {
                $j('#'+id).attr('src',pic1);
            }
        }


        function toggleDisplay(id) {
            if ($j('#'+id).css('display') === 'none') {
                $j('#'+id).css('display','block')
            } else {
                $j('#'+id).css('display','none')
            }
        }


        function showHoverColor(row) {
            $j('#'+row).attr('color',$j('#'+row).css('background-color'));
            $j('#'+row).css('background-color', '#cdebf2');
        }

        function showOriginalColor(row) {
            $j('#'+row).css('background-color', $j('#'+row).attr('color'));
        }

        function setupRow(row, color, result, status, statusOrder) {
            $j('#'+row).css('background-color',color);
            $j('#'+row).attr('color', color);
            $j('#'+row+"_result").html('<b>Test result</b><br />'+result);
            $j('#'+row+"_status").html(status);
            $j('#'+row).attr('status',statusOrder);
            sortList();
        }

        function resetRow(row) {
            setupRow(row, '#ffffff', 'No result exists.', 'Not run', 4);
        }


        function verifyData(cmp) {
            if (tests[testRunning].length > 0) {
                testname = tests[testRunning]
            } else {
                testname = 'base';
            }
            cmp = jQuery.parseJSON(cmp);
            if (cmp.data.more.length === 0 && cmp.data.less.length === 0) {
                setupRow(testname, '#b0e399', 'Perfect match.', 'OK', 3);
            } else if ((cmp.data.more.length > 0) && (cmp.data.less.length > 0)) {
                setupRow(testname, '#ff7f7f', getRepsonseAsText(cmp.data), 'Too few & too many', 1);
            } else if (cmp.data.more.length > 0) {
                setupRow(testname, '#ff9900', getRepsonseAsText(cmp.data), 'Too many', 2);
            } else {
                setupRow(testname, '#fdff7f', getRepsonseAsText(cmp.data), 'Too few', 2);
            }
            isLoggedIn = true;
            hideLogin();
            setTimeout("runNext()", 2000);
        }

        function getRepsonseAsText(data) {
            text = "";
            if (data.more.length>0) {
                text = "The following parameters should NOT be returned: \n<ul>\n";
                for(i=0;i<data.more.length;i++){
                    text += "<li>" + data.more[i] + "</li>\n";
                }
                text += "</ul>\n"
            }

            if (data.less.length>0) {
                text += "The following parameters should be returned: \n<ul>\n";
                for(i=0;i<data.less.length;i++){
                    text += "<li>" + data.less[i] + "</li>\n";
                }
                text += "</ul>\n"
            }
            return text;
        }

        function hideLogin() {
            $j("#background").hide();
            $j("#iframe").hide();
            $j("#iframeDescription").hide();
            $j('#execute').remove();
            $j(".container").show();
        }


        function showLogin() {
            if ($j('#execute').length > 0) {
                $j(".container").hide();
                $j("#background").show();
                $j("#iframe").show();
                $j("#iframeDescription").show();
                $j("#execute").show();
            }
        }

        function callIframe(id, url) {
            $j('#iframe').html('<IFRAME id="'+id+'" >');

            if (!isLoggedIn)
                showLogin();

            $j('iframe#'+id).attr('src', url);
        }

        function performTest(type) {
            callIframe('execute', "/ecat?c="+type);
        }

        function runNext() {
            if ((tests.length > 0) && (testRunning<(tests.length-1))){
                testRunning += 1;
                performTest(tests[testRunning]);
            } else {
                testRunning = -1;
                setNoTestIsRunning();
            }
        }

        function runTest(testname) {
            if (testIsRunning===false) {
                setTestIsRunning();
                testRunning = -1;
                tests = new Array();
                if (testname === "") {
                    resetRow("base");
                } else {
                    resetRow(testname);
                }
                tests.push(testname);
                runNext();
            }
        }

        function setNoTestIsRunning() {
            isLoggedIn = false;
            testIsRunning = false;
            $j('.btn').removeAttr('style');
            $j('#running_test').hide();
            if (sortOrder===sortByStatusValue) {
                sortByStatus();
            }
            sortList();
        }

        function setTestIsRunning() {
            testIsRunning = true;
            $j('.btn').attr('style','background-color:#c9c9c9;');
            $j('#running_test').show();
        }

        function runAll() {
            if (testIsRunning===false) {
                setTestIsRunning();
                testRunning = -1;
                tests = new Array();
                for(i=0;i<ec_seq.length;i++){
                    ec = ec_seq[i];
                    if (ec === "") {
                        resetRow("base");
                    } else {
                        resetRow(ec);
                    }
                    tests.push(ec);
                }
                runNext();
            }
        }

        function setupec_seq() {
            ec_seq = new Array();
            count = 0;
            $j('#rowContainer').children().each( function() {
                ec_seq[count] = $j(this).attr('id');
                count++;
            } );
        }

        function sortList() {
            $j('ul>li').tinysort();
        }


        function sortByName() {
            sortOrder=sortByNameValue;
            $j('#descHeader').css('text-decoration','underline');
            $j('#statusHeader').css('text-decoration','none');
            $j('div#rowContainer>div').tinysort('',{attr:'name'});
             setupec_seq();
        }

        function sortByStatus() {
            sortOrder=sortByStatusValue;
            $j('#descHeader').css('text-decoration','none');
            $j('#statusHeader').css('text-decoration','underline');
            $j('div#rowContainer>div').tinysort('',{attr:'status'});
            setupec_seq();
        }

        $j(document).ready(function() {
            $j('#iframe').width($j('html').width()-40);
            $j('#iframe').height($j('html').height()-140);
            $j('#iframeDescription').width($j('html').width()-40);
            $j('#iframeDescription').height(100);
            $j('#iframeDescription').css('margin-top',$j('html').height()-140+'px');
            sortByName();
            sortList();
        });

    </script>
</head>
    <body>
        <div id="background"></div>
        <div id="iframe"></div>
        <div id="iframeDescription">
            <h2><i>To continue the tests you first have to authenticate your self.</i></h2>
            <input type="button" value="Abort" onclick="hideLogin();setNoTestIsRunning();" >
        </div>

        <div class="container">
            <div class="navbar navbar-default">
                <div class="navbar-header">
                  <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                  </button>
                  <a class="navbar-brand" href="#"><img src="static/SWAMID.png" width="40" height="40" />
                      <span class="h1">Test utility for verifying your IdPs category compliance</span></a>
                </div>
            </div>
            <div id="formContainer" class="jumbotron" >
                <div id="running_test"><img src="static/loader.gif" />&nbsp;&nbsp;Wait while testing.</div>
                <span>This utility can test all IdP's contained in the metadata configured
                    for its service provider.</span><br />
                <span>An overview of test results from previously tested IdP's is available <a href="/overview">here</a></span><br>

                <span>NOTE:</span><br />
                <span>To run this utility your IdP must be allowed to be viewed in IFrames!</span><br />
                <span>Do not use X-Frame-Options in the HTTP response header or add ALLOW-FROM for samltest.swamid.se
                    in the X-Frame-Options.</span><br />
                <span id="helpLinkShow" class="link" onclick="toggleDisplay('help_instructions');
                                                      toggleDisplay('helpLinkShow');
                                                      toggleDisplay('helpLinkHide')">
                    <img src="static/arrowRight.png" /> Show instructions
                </span>
                <span id="helpLinkHide" style="display:none;" class="link" onclick="toggleDisplay('help_instructions');
                                                      toggleDisplay('helpLinkShow');
                                                      toggleDisplay('helpLinkHide')">
                    <img src="static/arrowDown.png" /> Hide instructions
                </span>
                <div id="help_instructions">
                    <span class="h2">Instructions</span><br />
                    <div class="row">
                        <div class="col-md-6">
                            To start a test click on the run test button on the row of the test you would like to run.
                            If you want to start all tests click on the Run all test button above the test list.
                            You will be prompted to choose the correct IdP and perform validation before the test begins.
                            If you want more information about a test or the response generated by a test click anywhere
                            on the row of the test.
                        </div>
                        <div class="col-md-6">
                            <div>
                                <span class="h3">Possible test status</span>
                                <table>
                                    <tr>
                                        <td><div id="notrun" class="status_help">Not run</div></td>
                                        <td>Test has not been run</td>
                                    </tr>
                                    <tr>
                                        <td><div id="ok" class="status_help">OK</div></td>
                                        <td>Test finished without errors</td>
                                    </tr>
                                    <tr>
                                        <td><div id="toofew" class="status_help">Too few</div></td>
                                        <td>Test returned too few values</td>
                                    </tr>
                                    <tr>
                                        <td><div id="toomany" class="status_help">Too many</div></td>
                                        <td>Test returned too many values</td>
                                    </tr>
                                    <tr>
                                        <td><div id="toomanyfew" class="status_help">Too few & too many</div></td>
                                        <td>Test returned too few and too many values</td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row" style="background-color:transparent">
                    <div class="col-md-10"><span class="h2">Available tests</span></div>
                    <div class="col-md-2"><div class="btn btn-lg btn-primary mainbtn" onclick="runAll();" >Run all tests</div></div>
                </div>
                <div>
                    <div class="row" style="background-color: #c9c9c9">
                        <div id="descHeader" class="col-md-7">Description&nbsp;<img src="static/arrowDown.png" class="sort" onclick="sortByName()"/></div>
                        <div id="statusHeader" class="col-md-3">Status&nbsp;<img src="static/arrowDown.png" class="sort" onclick="sortByStatus()"/></div>
                        <div class="col-md-2">Test</div>
                    </div>
                    <div id="rowContainer">
                    ${createTests(ec_seq, ec_info)}
                    </div>
                    <div class="row"></div>
                </div>
            </div>
        </div>
    </body>
</html>
