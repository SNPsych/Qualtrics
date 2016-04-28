<!DOCTYPE html>
<html>
<head lang="en">
    <meta charset="UTF-8">
    <title>The Latest Survey Reports of SleepVL</title>
    <link rel="stylesheet" href="css/sleepvl.css"/>
</head>
<body>
<div class="logo">
    <a href="http://www.med.monash.edu.au/">
        <img width="386" height="64" alt="Monash University, Medicine, Nursing and Health Sciences" src="images/monash-med-logo.jpg">
    </a>
</div>
<br/>
<div class="content">
    <h2>The Latest Survey Reports of SleepVL</h2>
    <table class="display_data_tab">
        <thead>
        <tr>
            <th>Patient ID</th>
            <th>Reports</th>
        </tr>
        </thead>
        <tbody>
        % for pid in patients:
        <tr>
            <td>
                ${pid['id']}
            </td>
            <td>
                <a href="reports/pdf/${pid['uuid']}.pdf"> PDF </a> | <a href="reports/html/${pid['uuid']}.html"> HTML </a>
             </td>
        </tr>
        % endfor
        </tbody>
    </table>
    <br/>
    <br/>
    <br/>
    <br/>
</div>

<br/>
<br/>
<br/>
<div id="footer">
    <a href="http://www.copyright.monash.edu.au/">Copyright</a> &copy; 2015
    <a href="http://www.monash.edu.au/">Monash University</a> ABN 12 377 614 012 &ndash;
    <a href="http://www.monash.edu.au/legals/">Caution</a> &ndash;
    <a href="http://www.monash.edu.au/legals/privacy.html">Privacy</a> &ndash;
    <a href="http://www.monash.edu.au/international/ausgov/">CRICOS Provider Number: 00008C</a>
    <br>
    Maintained by
    <a href="mailto:webmaster@med.monash.edu.au?subject=Web enquiry">webmaster@med.monash.edu.au</a> &ndash;
    <a href="http://www.monash.edu.au/accessibility/">Accessibility information</a>
    <br>
    <br>
</div>
</body>
</html>