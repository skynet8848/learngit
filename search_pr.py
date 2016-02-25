#!/usr/local/bin/python
from __future__ import division
import sys
import getpass
import re
import getopt
import commands
import time
import os
sys.path.append("/homes/ryanliu/python")
import httplib2
sys.path.append("/homes/ryanliu/python/chartdir")
from pychartdir import *

#Define the user list here which will be used as alias of the originator
amalik_team=["qzhu","hongh","cesarc","mmughal","amalik"]
shuang_team=["ryanliu","weizhao","mzhou","rdguo","zljin","arielwei","yangchen","arieszhan","darrenli","tommysun","lusiwang","emilydu","shuang"]
gshi_team=["alanzxc","andyhou","robinma","tinatong","gshi"]
jennyc_team=["sallyliu","wqian","xiangz","jennyc"]
hcl_team=["dhurgar","madhavann","nirmalrs","poornimg","rdeshmuk","smandela"]
platform_team=["anjalim","bsahu"]
            
SBU_PDT_team=shuang_team+gshi_team+amalik_team+jennyc_team+hcl_team

team_list=["amalik", "shuang","jennyc","gshi","hcl","SBU_PDT","platform"]

def query_PR_state_all(expr):
    query_format="""/usr/local/bin/query-pr -H gnats -P 1529 -f '"%s\\n%s\\n%s\\n%s State{1} open\\n%s\\n\\n\\n\\n" number reported-in category  arrival-date change-log' --table-format 'Change-log "%s %s %s %s\\n" Datetime Field From To'"""
    if not expr:
        #usage()   
        #sys.exit()
        PASS
    else:
        query_option="""-e '%s'""" % expr       
    query_command=query_format+' '+query_option
    #print query_command
    (status, output) = commands.getstatusoutput("""%s""" % query_command)
    if re.match(r'query-pr: no PRs matched', output):
        results=[]
        results.append([str(0),str(0),commands.getstatusoutput('date')[1]]) 
        data=[]
        return [results,data]
    else:
        output=output.strip()
        output=output.split('\n\n\n\n\n\n')
        data=[]
        data_all=[]
        pr_list=[]
        for i in range(len(output)):
            templist=output[i].split('\n')
            pr_number=templist[0]
            if not pr_number in pr_list:
                pr_list.append(pr_number)
                data.append(templist)
            data_all.append(templist)       
        results=[]
        results.append([str(len(data_all)),str(len(data)),commands.getstatusoutput('date')[1]]) 
        return [results,data]

def query_PR_all(synopsis,keyword,expr):
    query_format="""/usr/local/bin/query-pr -f '"%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n%s\\n\\n\\n" number synopsis reported-in submitter-id platform category problem-level problem-level blocker planned-release state responsible originator attributes arrival-date class'"""
    if not synopsis and not keyword and not expr:
        usage()   
        sys.exit()
    elif expr:
        query_option="""-e '%s'""" % expr
    else:      
        if not keyword:
            synopsisList=synopsis.split(',')
            if len(synopsisList)==1:
                query_option="""-e 'synopsis~"%s"'""" % synopsisList[0]
            else:
                for i in range(len(synopsisList)):
                    synopsisList[i]='synopsis~"%s"' % synopsisList[i]
                or_option=" | ".join(synopsisList)
                query_option="-e '%s'" % or_option
        elif not synopsis:
            keywordList=keyword.split(',')
            if len(keywordList)==1:
                query_option="""-e 'keywords~"%s"'""" % keywordList[0]
            else:
                for i in range(len(keywordList)):
                    keywordList[i]='keywords~"%s"' % keywordList[i]
                or_option=" | ".join(keywordList)
                query_option="-e '%s'" % or_option
        else:
                synopsisList=synopsis.split(',')
                keywordList=keyword.split(',')
                if len(synopsisList)==1 and len(keywordList)==1:
                    query_option="""-e 'synopsis~"%s" | keywords~"%s"'""" % (synopsisList[0],keywordList[0])
                elif len(synopsisList)==1 and not len(keywordList)==1:
                    for i in range(len(keywordList)):
                        keywordList[i]='keywords~"%s"' % keywordList[i]
                    or_option=" | ".join(keywordList)
                    query_option="""-e 'synopsis~"%s" | %s'""" % (synopsisList[0],or_option)
                elif not len(synopsisList)==1 and len(keywordList)==1:
                    for i in range(len(synopsisList)):
                        synopsisList[i]='synopsis~"%s"' % synopsisList[i]
                    or_option=" | ".join(synopsisList)
                    query_option="""-e 'keywords~"%s" | %s'""" % (keywordList[0],or_option)
                else:
                    for i in range(len(keywordList)):
                        keywordList[i]='keywords~"%s"' % keywordList[i]
                    or_option_keyword=" | ".join(keywordList)
                    for i in range(len(synopsisList)):
                        synopsisList[i]='synopsis~"%s"' % synopsisList[i]
                    or_option_synopsis=" | ".join(synopsisList)
                    query_option="-e '%s | %s'" % (or_option_keyword,or_option_synopsis)        
    query_command=query_format+' '+query_option
    #print query_command 
    (status, output) = commands.getstatusoutput("""%s""" % query_command)
    if re.match(r'query-pr: no PRs matched', output):
        results=[]
        results.append([str(0),str(0),commands.getstatusoutput('date')[1]]) 
        data=[]
        return [results,data]
    else:
        output=output.strip()
        output=output.split('\n\n\n\n')
        data=[]
        data_all=[]
        pr_list=[]
        for i in range(len(output)):
            templist=output[i].split('\n')
            pr_number=templist[0].split('-')[0]
            if not pr_number in pr_list:
                pr_list.append(pr_number)
                data.append(templist)
            data_all.append(templist)       
        results=[]
        results.append([str(len(data_all)),str(len(data)),commands.getstatusoutput('date')[1]]) 
        return [results,data]

def get_start_end_date(data):
    month = {"Jan"  : '01',
                 "Feb"  : '02',
                 "Mar"  : '03',
                 "Apr"  : '04',
                 "May"  : '05',
                 "Jun"  : '06',
                 "Jul"  : '07',
                 "Aug"  : '08',
                 "Sep"  : '09',
                 "Oct"  : '10',
                 "Nov"  : '11',
                 "Dec"  : '12',             
                 }
    if not data[1]:
        date=commands.getstatusoutput('date')[1].split(' ')
        start_date='%s-%s-%s' % (date[5],month[date[1]],date[2])
        end_date='%s-%s-%s' % (date[5],month[date[1]],date[2])
        return [start_date,end_date]
    else:
        date=data[1][0][14].split(' ')    
        start_date='%s-%s-%s' % (date[5],month[date[1]],date[2])
        date=data[1][-1][14].split(' ')    
        end_date='%s-%s-%s' % (date[5],month[date[1]],date[2])
        return [start_date,end_date]
        
def get_date_list(start_date,end_date,duration=16):
    ISOTIMEFORMAT='%Y-%m-%d'
    timelist=[int(start_date.split('-')[0]),int(start_date.split('-')[1]),int(start_date.split('-')[2]),0,0,0,0,0,0]
    start_time=time.mktime(timelist)
    end_date_list=[]
    for i in range(duration):
        end_date_list.append(time.strftime(ISOTIMEFORMAT,time.gmtime(start_time+86400*7*(i+1))))
    timelist=[int(end_date.split('-')[0]),int(end_date.split('-')[1]),int(end_date.split('-')[2]),0,0,0,0,0,0]
    end_time=time.mktime(timelist)
    timelist=[int(end_date_list[-1].split('-')[0]),int(end_date_list[-1].split('-')[1]),int(end_date_list[-1].split('-')[2]),0,0,0,0,0,0]
    last_time=time.mktime(timelist)
    if last_time<end_time:
        end_date_list.append(time.strftime(ISOTIMEFORMAT,time.gmtime(end_time+86400)))
    return end_date_list

def adjust_start_date(start_date):
    ISOTIMEFORMAT='%Y-%m-%d'
    timelist=[int(start_date.split('-')[0]),int(start_date.split('-')[1]),int(start_date.split('-')[2]),0,0,0,0,0,0]
    start_time=time.mktime(timelist)
    adjust_start_date=time.strftime(ISOTIMEFORMAT,time.gmtime(start_time-86400*7))
    return adjust_start_date
    
def get_time(date):
    ISOTIMEFORMAT='%Y-%m-%d'
    timelist=[int(date.split('-')[0]),int(date.split('-')[1]),int(date.split('-')[2]),0,0,0,0,0,0]
    time_number=time.mktime(timelist)
    return time_number
    
def query_PR_weekly(data,start_date,end_date):
    month = {"Jan"  : '01',
                 "Feb"  : '02',
                 "Mar"  : '03',
                 "Apr"  : '04',
                 "May"  : '05',
                 "Jun"  : '06',
                 "Jul"  : '07',
                 "Aug"  : '08',
                 "Sep"  : '09',
                 "Oct"  : '10',
                 "Nov"  : '11',
                 "Dec"  : '12',             
                 }
    if not data[1]:
        results=[]
        results.append([str(0),str(0),commands.getstatusoutput('date')[1]]) 
        data=[]
        total_number=0
        blocker_number=0
        info_feedback_number=0
        open_number=0
        closed_number=0
        return [total_number,blocker_number,info_feedback_number,open_number,closed_number]
    else:
        data_weekly=[]
        start_time=get_time(start_date)
        end_time=get_time(end_date)
        for i in range(len(data[1])):
            dateList=data[1][i][14].split(' ')
            format_date='%s-%s-%s' % (dateList[5],month[dateList[1]],dateList[2])
            if start_time<=get_time(format_date) and end_time>get_time(format_date):
                data_weekly.append(data[1][i])
        total_number=len(data_weekly)
        blocker_number=0
        info_feedback_number=0
        open_number=0
        closed_number=0
        for i in range(len(data_weekly)):
            if data_weekly[i][8]:
                blocker_number+=1
            if data_weekly[i][10] in ['need-info','feedback']:
                info_feedback_number+=1   
            if data_weekly[i][10] in ['open']:
                open_number+=1
            if data_weekly[i][10] in ['closed']:
                closed_number+=1
        return [total_number,blocker_number,info_feedback_number,open_number,closed_number]

def usage():
    print """\
    This program searchs PR status in https://gnats.juniper.net with the user name as the originator option.
    Options include:
    -v or --version       : Prints the version number
    -h or --help          : Display this help
    -e or --expr          : Specifies the expressions for query (no default value)
    -s or --synopsis      : Specifies the content in the synopsis used for query (no default value)
    -k or --keyword       : Specifies the keyword used for query (no default value)
    -o or --originator    : Specifies the list of the originator (default is all originators)
    -w or --weeks         : Specifies the number of weeks used in weekly trending chart (default is 16 weeks)
    -d or --dir           : Specifies the directory name at ~/public_html for saving the query result (default is the version number in the synopsis or keyword)
    -t or --title         : Specifies the title name of the chart (default name is 'SBU PDT')
    -a or --arrived-after : Specifies the start date of the trending chart wiht the format such as '2011-06-01' (default is the arrived date of the first PR)
    
    At least one of expr or synopsis or keyword must be specified, when use expr, the dir must be apecified.
    Example: use the expressions match the PRs in which Synopsis started with "Viking11.4" and "regression-pr" in Attributes and Class value is "bug", save the result at ~/public_html/11.4_regression_bug
    ./search_pr.py -e 'attributes~"regression-pr" & synopsis~"^Viking11.4" & class=="bug"' -d 11.4_regression_bug
    
    Alias can be used for multiple users as the originator option:
    Valid alias: shuang-team,amalik-team,gshi-team,jennyc-team,hcl-team,pdt-team
    """
def example():
    print """    
    Example 1. Search PR status from 11.2 to 11.4 and generate Web page http://www-in.juniper.net/~ryanliu/11.2-11.4/:
    http://www-in.juniper.net/~ryanliu/11.2-11.4/index.html            (14 statistics charts in this page)
    http://www-in.juniper.net/~ryanliu/11.2-11.4/all.html              (digest page of all PRs)
    http://www-in.juniper.net/~ryanliu/11.2-11.4/open.html             (digest page of open PRs)
    http://www-in.juniper.net/~ryanliu/11.2-11.4/info_feedback.html    (digest page of info and feedback PRs)
    http://www-in.juniper.net/~ryanliu/11.2-11.4/blocker.html          (digest page of blocker PRs)
    http://www-in.juniper.net/~ryanliu/11.2-11.4/search_pr.log         (log of the script)
    [ryanliu@ipg-pool1-02->/homes/ryanliu/python]>>./search_pr.py -s 'Viking11.2 SLT,Viking11.3 SLT,Viking11.4 SLT' -w 36 -d 11.2-11.4 -t 'SBU PDT 11.2 to 11.4'  

    JUNOS 11.2-11.4 statistics at Mon Jun 27 04:08:17 PDT 2011
    ===============================================================================================
    Total    Open    Info    Analyzed    Assigned    Feedback    Monitored    Closed    Originator
    ===============================================================================================
       68       7       3           0            0           0            9        49    emilydu
       42       8       0           0            0           0            0        34    cesarc
       40       0       0           0            0           0            0        40    ryanliu
       36       6       0           0            0           0            0        30    qzhu
       34       1       0           1            0           1            3        28    tommysun
       32       0       0           2            0           0            0        30    weizhao
       28       4       0           0            0           0            3        21    darrenli
       22       0       2           2            0           0            0        18    arieszhan
       19       0       0           0            0           0            0        19    mmughal
       17       1       1           0            0           0            3        12    zljin
       12       1       0           0            0           0            0        11    hongh
       12       1       0           0            0           0            1        10    lusiwang
       12       0       0           0            0           0            0        12    mzhou
        9       2       0           0            0           0            2         5    rdguo
        8       0       0           0            0           0            0         8    poornimg
        8       0       0           0            0           0            1         7    yangchen
        7       1       0           0            0           0            1         5    dhurgar
        6       0       0           0            0           0            1         5    nirmalrs
        3       0       1           0            0           1            0         1    arielwei
        2       0       0           0            0           0            0         2    amalik
        2       0       0           0            0           0            0         2    smandela
        1       0       0           0            0           0            0         1    yangjun
    ===============================================================================================
      420      32       7           5            0           2           24       350    Summary
    ===============================================================================================
    [ryanliu@ipg-pool1-02->/homes/ryanliu/python]>>
    
    Example 2. Search PR status from 11.4 to 12.1 for spark and jenny team and generate Web page and generate Web page http://www-in.juniper.net/~ryanliu/11.4-12.1
    [ryanliu@ipg-pool1-02->/homes/ryanliu/python]>>./search_pr.py -s 'Viking11.4 SLT' -k '12.1sbupdt' -w 16 -d 11.4-12.1 -o shuang-team,jennyc-team

    JUNOS 11.4-12.1 statistics at Mon Jun 27 04:25:04 PDT 2011
    ===============================================================================================
    Total    Open    Info    Analyzed    Assigned    Feedback    Monitored    Closed    Originator
    ===============================================================================================
        7       0       0           0            0           0            0         7    ryanliu
        6       0       0           1            0           0            0         5    weizhao
        0       0       0           0            0           0            0         0    mzhou
        4       0       0           0            0           0            1         3    rdguo
        4       1       1           0            0           0            0         2    zljin
        0       0       0           0            0           0            0         0    arielwei
        3       0       0           0            0           0            0         3    yangchen
        9       0       2           0            0           0            0         7    arieszhan
       11       2       0           0            0           0            1         8    darrenli
       15       1       0           1            0           1            1        11    tommysun
        1       1       0           0            0           0            0         0    lusiwang
       26       1       0           0            0           0            1        24    emilydu
        0       0       0           0            0           0            0         0    shuang
        3       0       0           0            0           2            0         1    sallyliu
        0       0       0           0            0           0            0         0    wqian
        0       0       0           0            0           0            0         0    xiangz
        0       0       0           0            0           0            0         0    jennyc
    ===============================================================================================
       89       6       3           2            0           3            4        71    Summary
    ===============================================================================================
    [ryanliu@ipg-pool1-02->/homes/ryanliu/python]>>"""

def trendingLine(total_list,blocker_list,info_feedback_list,end_date_list,title,title2,version,name):
    # The data for the chart  
    data0 = total_list 
    data1 = blocker_list
    data2 = info_feedback_list
    labels = end_date_list

    # Create a XYChart object of size 600 x 360 pixels. Set background color to brushed
    # silver, with a 2 pixel 3D border. Use rounded corners.
    
    if len(end_date_list)>21:
        c = XYChart(1200, 320, brushedSilverColor(), Transparent, 2)
    else:
        c = XYChart(600, 320, brushedSilverColor(), Transparent, 2) 
    #c.setBackground(c.linearGradientColor(0, 0, 0, 100, '0x99ccff', '0xffffff'),
    #'0x888888')
    c.setRoundedFrame()
    c.setDropShadow()
 

    # Add a title to the chart using 15pts Times Bold Italic font, with a light blue
    # (ccccff) background and with glass lighting effects.
    title = c.addTitle("%s" % title, "timesbi.ttf", 15,'0xffffff')
    title.setBackground('0x0000cc', '0x000000', glassEffect(ReducedGlare))
    if len(end_date_list)>21:
        timeStamp = c.addText(1170, 318, "%s" % title2, "arialbd.ttf")
    else:
        timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    timeStamp.setAlignment(BottomRight)

    # Add a separator line just under the title
    #c.addLine(10, title.getHeight(), c.getWidth() - 11, title.getHeight(), LineColor)

    # Add a legend box where the top-center is anchored to the horizontal center of the
    # chart, just under the title. Use horizontal layout and 10 points Arial Bold font,
    # and transparent background and border.
    legendBox = c.addLegend(c.getWidth() / 2, title.getHeight(), 0, "arialbd.ttf", 10)
    legendBox.setAlignment(TopCenter)
    legendBox.setBackground(Transparent, Transparent)

    # Tentatively set the plotarea at (70, 75) and of 460 x 240 pixels in size. Use
    # transparent border and black (000000) grid lines
    if len(end_date_list)>21:
        c.setPlotArea(70, 75, 920, 240, -1, -1, Transparent, '0x000000', -1)
    else:
        c.setPlotArea(70, 75, 460, 240, -1, -1, Transparent, '0x000000', -1)

    # Set the x axis labels
    c.xAxis().setLabels(labels).setFontAngle(45)

    # Show the same scale on the left and right y-axes
    c.syncYAxis()

    # Set y-axis tick density to 30 pixels. ChartDirector auto-scaling will use this as
    # the guideline when putting ticks on the y-axis.
    c.yAxis().setTickDensity(30)

    # Set all axes to transparent
    c.xAxis().setColors(Transparent)
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)

    # Set the x-axis margins to 15 pixels, so that the horizontal grid lines can extend
    # beyond the leftmost and rightmost vertical grid lines
    c.xAxis().setMargin(15, 15)

    # Set axis label style to 8pts Arial Bold
    c.xAxis().setLabelStyle("arialbd.ttf", 8).setFontAngle(45)
    c.yAxis().setLabelStyle("arialbd.ttf", 8)
    c.yAxis2().setLabelStyle("arialbd.ttf", 8)

    # Add axis title using 10pts Arial Bold Italic font
    c.yAxis().setTitle("PR Number", "arialbi.ttf", 10)
    c.yAxis2().setTitle("PR Number", "arialbi.ttf", 10)
    c.yAxis().setMinTickInc(1)
    c.yAxis2().setMinTickInc(1)
    # Add the first line. The missing data will be represented as gaps in the line (the
    # default behaviour)
    layer0 = c.addLineLayer2()
    layer0.addDataSet(data0, '0x00ff00', "Weekly PRs").setDataSymbol(
    GlassSphere2Shape, 11)
    layer0.setLineWidth(3)

    # Add the second line. The missing data will be represented by using dash lines to
    # bridge the gap
    layer1 = c.addLineLayer2()
    layer1.addDataSet(data1, '0xff0000', "Blocker PRs").setDataSymbol(
    GlassSphere2Shape, 11)
    layer1.setLineWidth(3)
    layer1.setGapColor(c.dashLineColor('0x00ff00'))

    # Add the third line. The missing data will be ignored - just join the gap with the
    # original line style.
    layer2 = c.addLineLayer2()
    layer2.addDataSet(data2, '0xff6600', "Info and Feedback PRs").setDataSymbol(
    GlassSphere2Shape, 11)
    layer2.setLineWidth(3)
    layer2.setGapColor(SameAsMainColor)

    # layout the legend so we can get the height of the legend box
    c.layoutLegend()

    # Adjust the plot area size, such that the bounding box (inclusive of axes) is 15
    # pixels from the left edge, just under the legend box, 16 pixels from the right
    # edge, and 25 pixels from the bottom edge.
    c.packPlotArea(15, legendBox.getTopY() + legendBox.getHeight(), c.getWidth() - 16,
    c.getHeight() - 25)

    # Output the chart
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    c.makeChart("/homes/%s/public_html/%s/%s.png" % (user,version[0],name))

def trendingLine_all(all_list,all_closed_list,all_blocker_list,end_date_list,title,title2,version,name):
    # The data for the chart  
    data0 = all_list 
    data1 = all_closed_list
    data2 = all_blocker_list
    labels = end_date_list

    # Create a XYChart object of size 600 x 360 pixels. Set background color to brushed
    # silver, with a 2 pixel 3D border. Use rounded corners.
    
    if len(end_date_list)>21:
        c = XYChart(1200, 320, brushedSilverColor(), Transparent, 2)
    else:
        c = XYChart(600, 320, brushedSilverColor(), Transparent, 2)    
    #c.setBackground(c.linearGradientColor(0, 0, 0, 100, '0x99ccff', '0xffffff'),
    #'0x888888')
    c.setRoundedFrame()
    c.setDropShadow()
 

    # Add a title to the chart using 15pts Times Bold Italic font, with a light blue
    # (ccccff) background and with glass lighting effects.
    title = c.addTitle("%s" % title, "timesbi.ttf", 15,'0xffffff')
    title.setBackground('0x0000cc', '0x000000', glassEffect(ReducedGlare))
    #timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    if len(end_date_list)>21:
        timeStamp = c.addText(1170, 318, "%s" % title2, "arialbd.ttf")
    else:
        timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    timeStamp.setAlignment(BottomRight)

    # Add a separator line just under the title
    #c.addLine(10, title.getHeight(), c.getWidth() - 11, title.getHeight(), LineColor)

    # Add a legend box where the top-center is anchored to the horizontal center of the
    # chart, just under the title. Use horizontal layout and 10 points Arial Bold font,
    # and transparent background and border.
    legendBox = c.addLegend(c.getWidth() / 2, title.getHeight(), 0, "arialbd.ttf", 10)
    legendBox.setAlignment(TopCenter)
    legendBox.setBackground(Transparent, Transparent)

    # Tentatively set the plotarea at (70, 75) and of 460 x 240 pixels in size. Use
    # transparent border and black (000000) grid lines
    if len(end_date_list)>21:
        c.setPlotArea(70, 75, 920, 240, -1, -1, Transparent, '0x000000', -1)
    else:
        c.setPlotArea(70, 75, 460, 240, -1, -1, Transparent, '0x000000', -1)
    
    # Set the x axis labels
    c.xAxis().setLabels(labels).setFontAngle(45)

    # Show the same scale on the left and right y-axes
    c.syncYAxis()

    # Set y-axis tick density to 30 pixels. ChartDirector auto-scaling will use this as
    # the guideline when putting ticks on the y-axis.
    c.yAxis().setTickDensity(30)

    # Set all axes to transparent
    c.xAxis().setColors(Transparent)
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)

    # Set the x-axis margins to 15 pixels, so that the horizontal grid lines can extend
    # beyond the leftmost and rightmost vertical grid lines
    c.xAxis().setMargin(15, 15)

    # Set axis label style to 8pts Arial Bold
    c.xAxis().setLabelStyle("arialbd.ttf", 8).setFontAngle(45)
    c.yAxis().setLabelStyle("arialbd.ttf", 8)
    c.yAxis2().setLabelStyle("arialbd.ttf", 8)

    # Add axis title using 10pts Arial Bold Italic font
    c.yAxis().setTitle("PR Number", "arialbi.ttf", 10)
    c.yAxis2().setTitle("PR Number", "arialbi.ttf", 10)
    c.yAxis().setMinTickInc(1)
    c.yAxis2().setMinTickInc(1)
    # Add the first line. The missing data will be represented as gaps in the line (the
    # default behaviour)
    layer0 = c.addLineLayer2()
    layer0.addDataSet(data0, '0xff6600', "Total PRs").setDataSymbol(
    GlassSphere2Shape, 11)
    layer0.setLineWidth(3)

    # Add the second line. The missing data will be represented by using dash lines to
    # bridge the gap
    layer1 = c.addLineLayer2()
    layer1.addDataSet(data1, '0x00ff00', "Closed PRs").setDataSymbol(
    GlassSphere2Shape, 11)
    layer1.setLineWidth(3)
    layer1.setGapColor(c.dashLineColor('0x00ff00'))

    # Add the third line. The missing data will be ignored - just join the gap with the
    # original line style.
    layer2 = c.addLineLayer2()
    layer2.addDataSet(data2, '0xff0000', "Blocker PRs").setDataSymbol(
    GlassSphere2Shape, 11)
    layer2.setLineWidth(3)
    layer2.setGapColor(SameAsMainColor)

    # layout the legend so we can get the height of the legend box
    c.layoutLegend()

    # Adjust the plot area size, such that the bounding box (inclusive of axes) is 15
    # pixels from the left edge, just under the legend box, 16 pixels from the right
    # edge, and 25 pixels from the bottom edge.
    c.packPlotArea(15, legendBox.getTopY() + legendBox.getHeight(), c.getWidth() - 16,
    c.getHeight() - 25)

    # Output the chart
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    c.makeChart("/homes/%s/public_html/%s/%s.png" % (user,version[0],name))

def stackedBar(closed,open,info,feedback,monitored,analyzed,assigned,labels,title,title2,version):
    #info = [10,20,30]
    #feedback = [15,12,23]
    #open = [6,9,7]
    #labels = ["ryanliu", "mzhou", "zljin"]
    #
    # Now we have read data into arrays, we can draw the chart using ChartDirector
    # 
    # Create a XYChart object of size 600 x 320 pixels, with a light grey (eeeeee)
    # background, black border, 1 pixel 3D border effect and rounded corners.
    
    if len(labels)>30:
        c = XYChart(1200, 320, brushedSilverColor(), Transparent, 2)
    else:
        c = XYChart(600, 320, brushedSilverColor(), Transparent, 2)
    #c = XYChart(600, 320, '0xeeeeee', '0x000000', 1)
    #c.setBackground(c.linearGradientColor(0, 0, 0, 100, '0x99ccff', '0xffffff'),
    #'0x888888')
    c.setRoundedFrame()
    c.setDropShadow()

    # Set the plotarea at (60, 60) and of size 520 x 200 pixels. Set background color to
    # white (ffffff) and border and grid colors to grey (cccccc)
    #c.setPlotArea(37, 37, 520, 200, Transparent, -1, ''0x000000'', ''0x000000'')
    if len(labels)>30:
        c.setPlotArea(50, 60, 500, 200, -1, -1, Transparent, '0x000000', -1)
    else:
        c.setPlotArea(50, 60, 1100, 200, -1, -1, Transparent, '0x000000', -1)
    # Set the x axis labels
    c.xAxis().setLabels(labels).setFontAngle(45)

    # Show the same scale on the left and right y-axes
    c.syncYAxis()

    # Set y-axis tick density to 30 pixels. ChartDirector auto-scaling will use this as
    # the guideline when putting ticks on the y-axis.
    c.yAxis().setTickDensity(30)

    # Set all axes to transparent
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)

    # Set the x-axis margins to 15 pixels, so that the horizontal grid lines can extend
    # beyond the leftmost and rightmost vertical grid lines
    c.xAxis().setMargin(15, 15)

    # Set axis label style to 8pts Arial Bold
    c.xAxis().setLabelStyle("arialbd.ttf", 8).setFontAngle(45)
    c.yAxis().setLabelStyle("arialbd.ttf", 8)
    c.yAxis2().setLabelStyle("arialbd.ttf", 8)

    # Add axis title using 10pts Arial Bold Italic font
    c.yAxis().setTitle("PR Number", "arialbi.ttf", 10)
    c.yAxis2().setTitle("PR Number", "arialbi.ttf", 10)
    c.yAxis().setMinTickInc(1)
    c.yAxis2().setMinTickInc(1)


    # Add a title to the chart using 15pts Times Bold Italic font, with a light blue
    # (ccccff) background and with glass lighting effects.
    title = c.addTitle("%s" % title, "timesbi.ttf", 15,'0xffffff')
    title.setBackground('0x0000cc', '0x000000', glassEffect(ReducedGlare))
    if len(labels)>30:
        timeStamp = c.addText(1170, 318, "%s" % title2, "arialbd.ttf")
    else:
        timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    timeStamp.setAlignment(BottomRight)

    # Add a legend box at (70, 32) (top of the plotarea) with 9pts Arial Bold font
    legendBox = c.addLegend(c.getWidth() / 2, title.getHeight(), 0, "arialbd.ttf", 8)
    legendBox.setAlignment(TopCenter)
    legendBox.setBackground(Transparent, Transparent)

    # Add a stacked bar chart layer using the supplied data
    layer = c.addBarLayer2(Stack)
    layer.addDataSet(closed, '0x66aaee', "Closed")
    layer.addDataSet(open, '0xeebb22', "Open")
    layer.addDataSet(info, '0xbbbbbb', "Info")
    layer.addDataSet(feedback, '0x8844ff', "Feedback")
    layer.addDataSet(monitored, '0xdd2222', "Monitored")
    layer.addDataSet(analyzed, '0x0000ff', "Analyzed")
    layer.addDataSet(assigned, '0x00ffff', "Assigned")
    
    # Use soft lighting effect with light direction from the left
    layer.setBorderColor(Transparent, softLighting(Left))

    # Set the x axis labels. In this example, the labels must be Jan - Dec.

    #c.xAxis().setLabels(labels).setFontAngle(40)

    # Draw the ticks between label positions (instead of at label positions)
    #c.xAxis().setTickOffset(0.5)

    # Set the y axis title
    #c.yAxis().setTitle("PR Number")
    #c.yAxis().setMinTickInc(1)
    #c.yAxis2().setTitle("PR Number")
    #c.yAxis2().setMinTickInc(1)
    # Set axes width to 2 pixels
    #c.xAxis().setWidth(2)
    #c.yAxis().setWidth(2)
    #c.yAxis2().setWidth(2)
    c.packPlotArea(15, title.getHeight() + legendBox.getHeight()+30, c.getWidth() - 16,
    c.getHeight() - 25)
    # Output the chart
    #c.makeChart("/homes/%s/public_html/image/stackedbar.png" % user)
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    c.makeChart("/homes/%s/public_html/%s/stackedbar.png" % (user,version[0]))

def stackedBar_responsible(info,feedback,monitored,labels,title,title2,version):
    #info = [10,20,30]
    #feedback = [15,12,23]
    #open = [6,9,7]
    #labels = ["ryanliu", "mzhou", "zljin"]
    #
    # Now we have read data into arrays, we can draw the chart using ChartDirector
    # 
    # Create a XYChart object of size 600 x 320 pixels, with a light grey (eeeeee)
    # background, black border, 1 pixel 3D border effect and rounded corners.
    
    if len(labels)>30:
        c = XYChart(1200, 320, brushedSilverColor(), Transparent, 2)
    else:
        c = XYChart(600, 320, brushedSilverColor(), Transparent, 2)
    #c = XYChart(600, 320, '0xeeeeee', '0x000000', 1)
    #c.setBackground(c.linearGradientColor(0, 0, 0, 100, '0x99ccff', '0xffffff'),
    #'0x888888')
    c.setRoundedFrame()
    c.setDropShadow()

    # Set the plotarea at (60, 60) and of size 520 x 200 pixels. Set background color to
    # white (ffffff) and border and grid colors to grey (cccccc)
    #c.setPlotArea(37, 37, 520, 200, Transparent, -1, ''0x000000'', ''0x000000'')
    if len(labels)>30:
        c.setPlotArea(50, 60, 500, 200, -1, -1, Transparent, '0x000000', -1)
    else:
        c.setPlotArea(50, 60, 1100, 200, -1, -1, Transparent, '0x000000', -1)
    # Set the x axis labels
    c.xAxis().setLabels(labels).setFontAngle(45)

    # Show the same scale on the left and right y-axes
    c.syncYAxis()

    # Set y-axis tick density to 30 pixels. ChartDirector auto-scaling will use this as
    # the guideline when putting ticks on the y-axis.
    c.yAxis().setTickDensity(30)

    # Set all axes to transparent
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)

    # Set the x-axis margins to 15 pixels, so that the horizontal grid lines can extend
    # beyond the leftmost and rightmost vertical grid lines
    c.xAxis().setMargin(15, 15)

    # Set axis label style to 8pts Arial Bold
    c.xAxis().setLabelStyle("arialbd.ttf", 8).setFontAngle(45)
    c.yAxis().setLabelStyle("arialbd.ttf", 8)
    c.yAxis2().setLabelStyle("arialbd.ttf", 8)

    # Add axis title using 10pts Arial Bold Italic font
    c.yAxis().setTitle("PR Number", "arialbi.ttf", 10)
    c.yAxis2().setTitle("PR Number", "arialbi.ttf", 10)
    c.yAxis().setMinTickInc(1)
    c.yAxis2().setMinTickInc(1)


    # Add a title to the chart using 15pts Times Bold Italic font, with a light blue
    # (ccccff) background and with glass lighting effects.
    title = c.addTitle("%s" % title, "timesbi.ttf", 15,'0xffffff')
    title.setBackground('0x0000cc', '0x000000', glassEffect(ReducedGlare))
    if len(labels)>30:
        timeStamp = c.addText(1170, 318, "%s" % title2, "arialbd.ttf")
    else:
        timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    timeStamp.setAlignment(BottomRight)

    # Add a legend box at (70, 32) (top of the plotarea) with 9pts Arial Bold font
    legendBox = c.addLegend(c.getWidth() / 2, title.getHeight(), 0, "arialbd.ttf", 8)
    legendBox.setAlignment(TopCenter)
    legendBox.setBackground(Transparent, Transparent)

    # Add a stacked bar chart layer using the supplied data
    layer = c.addBarLayer2(Stack)
    #layer.addDataSet(closed, '0x66aaee', "Closed")
    #layer.addDataSet(open, '0xeebb22', "Open")
    layer.addDataSet(info, '0xbbbbbb', "Info")
    layer.addDataSet(feedback, '0x8844ff', "Feedback")
    layer.addDataSet(monitored, '0xff6600', "Monitored")
    #layer.addDataSet(analyzed, '0x009900', "Analyzed")
    #layer.addDataSet(assigned, '0x00ffff', "Assigned")
    
    # Use soft lighting effect with light direction from the left
    layer.setBorderColor(Transparent, softLighting(Left))

    # Set the x axis labels. In this example, the labels must be Jan - Dec.

    #c.xAxis().setLabels(labels).setFontAngle(40)

    # Draw the ticks between label positions (instead of at label positions)
    #c.xAxis().setTickOffset(0.5)

    # Set the y axis title
    #c.yAxis().setTitle("PR Number")
    #c.yAxis().setMinTickInc(1)
    #c.yAxis2().setTitle("PR Number")
    #c.yAxis2().setMinTickInc(1)
    # Set axes width to 2 pixels
    #c.xAxis().setWidth(2)
    #c.yAxis().setWidth(2)
    #c.yAxis2().setWidth(2)
    c.packPlotArea(15, title.getHeight() + legendBox.getHeight()+30, c.getWidth() - 16,
    c.getHeight() - 25)
    # Output the chart
    #c.makeChart("/homes/%s/public_html/image/stackedbar.png" % user)
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    c.makeChart("/homes/%s/public_html/%s/stackedbar_responsible.png" % (user,version[0]))
   
def legendPie2(data,labels,title,title2,version,name):
    # The data for the pie chart
    #data = [21, 18, 15, 12, 2, 5,40]

    # The labels for the pie chart
    #labels = ["Closed","Open","Info","Feedback","Monitored","Analyzed","Assigned"]

    # The colors to use for the sectors
    colors = ['0x66aaee', '0xeebb22', '0xbbbbbb', '0x8844ff', '0xff6600', '0x0000ff', '0x00ffff']

    # Create a PieChart object of size 600 x 320 pixels. Use a vertical gradient color
    # from light blue (99ccff) to white (ffffff) spanning the top 100 pixels as
    # background. Set border to grey (888888). Use rounded corners. Enable soft drop
    # shadow.
    
    c = PieChart(600, 320, brushedSilverColor(), Transparent, 2)
    #c = PieChart(600, 320)
    #c.setBackground(c.linearGradientColor(0, 0, 0, 100, '0x99ccff', '0xffffff'),
    #    '0x888888')
    c.setRoundedFrame()
    c.setDropShadow()

    # Add a title using 18 pts Times New Roman Bold Italic font. Add 16 pixels top margin
    # to the title.
    title = c.addTitle("%s" % title, "timesbi.ttf", 15,'0xffffff')
    title.setBackground('0x0000cc', '0x000000', glassEffect(ReducedGlare))
    #c.addTitle2(Bottom, "%s" % title2, "ariali.ttf", 10).setBackground('0xccccff')
    timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    timeStamp.setAlignment(BottomRight)
    # Set the center of the pie at (160, 165) and the radius to 110 pixels
    c.setPieSize(160, 165, 110)

    # Draw the pie in 3D with a pie thickness of 25 pixels
    c.set3D(15)

    # Set the pie data and the pie labels
    c.setData(data, labels)

    # Set the sector colors
    c.setColors2(DataColor, colors)

    # Use local gradient shading for the sectors
    c.setSectorStyle(LocalGradientShading)

    # Use the side label layout method, with the labels positioned 16 pixels from the pie
    # bounding box
    c.setLabelLayout(SideLayout, 16)

    # Show only the sector number as the sector label
    c.setLabelFormat("{={sector}+1}")

    # Set the sector label style to Arial Bold 10pt, with a dark grey (444444) border
    c.setLabelStyle("arialbd.ttf", 10).setBackground(Transparent, '0x444444')

    # Add a legend box, with the center of the left side anchored at (330, 175), and
    # using 10 pts Arial Bold Italic font
    b = c.addLegend(330, 170, 1, "arialbi.ttf", 8)
    b.setAlignment(Left)

    # Set the legend box border to dark grey (444444), and with rounded conerns
    b.setBackground(Transparent, '0x444444')
    b.setRoundedCorners()

    # Set the legend box margin to 16 pixels, and the extra line spacing between the
    # legend entries as 5 pixels
    b.setMargin(16)
    b.setKeySpacing(0, 5)

    # Set the legend box icon to have no border (border color same as fill color)
    b.setKeyBorder(SameAsMainColor)

    # Set the legend text to show the sector number, followed by a 120 pixels wide block
    # showing the sector label, and a 40 pixels wide block showing the percentage
    b.setText(
        "<*block,valign=top*>{={sector}+1}.<*advanceTo=22*><*block,width=120*>{label}" \
        "<*/*><*block,width=40,halign=right*>{percent}<*/*>%")

    # Output the chart
    #c.makeChart("/homes/%s/public_html/image/legendpie2.png" % user)
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    c.makeChart("/homes/%s/public_html/%s/%s.png" % (user,version[0],name))

def cylinderlightbar(data,labels,title,title2,version,name):
    # The data for the bar chart
    #data = ['13', '9', '8', '6', '6', '5', '5', '5', '5', '5']*4

    # The labels for the bar chart
    #labels = ['sw-jsr-flow=13', 'sw-jsr-vpn=9', 'sw-viking-gprs=8', 'sw-slb-flow=6', 'sw-snmp=6', 'sw-australia-platform=5', 'sw-jsr-appfw=5', 'sw-jsr-ha=5', 'sw-srx-ipv6-flow=5', 'sw-jsr-appqos=5']*4

    # Create a XYChart object of size 600 x 320 pixels, with a light grey (eeeeee)
    # background, black border, 1 pixel 3D border effect and rounded corners.
    
    if len(labels)>21:
        c = XYChart(1200, 320, brushedSilverColor(), Transparent, 2)
    else:
        c = XYChart(600, 320, brushedSilverColor(), Transparent, 2)
    c.setRoundedFrame()
    c.setDropShadow()
    # Add a title to the chart using 18pts Times Bold Italic font. Set top/bottom margins
    # to 8 pixels.
    title = c.addTitle("%s" % title, "timesbi.ttf", 15,'0xffffff')
    title.setBackground('0x0000cc', '0x000000', glassEffect(ReducedGlare))
    if len(labels)>21:
        timeStamp = c.addText(1130, 45, "%s" % title2, "arialbd.ttf")
    else:
        timeStamp = c.addText(530, 45, "%s" % title2, "arialbd.ttf")
    timeStamp.setAlignment(BottomRight)

    # Set the plotarea at (70, 55) and of size 460 x 280 pixels. Use transparent border
    # and black grid lines. Use rounded frame with radius of 20 pixels.
    if len(labels)>21:
        c.setPlotArea(70, 48, 1060, 140, -1, -1, Transparent)
    else:
        c.setPlotArea(70, 48, 460, 140, -1, -1, Transparent)
    #c.setRoundedFrame('0xffffff', 20)

    # Add a multi-color bar chart layer using the supplied data. Set cylinder bar shape.
    c.addBarLayer3(data).setBarShape(CircleShape)
    layer = c.addBarLayer(data, c.gradientColor(100, 0, 500, 0, '0x008000', '0xffffff'))
    layer.setAggregateLabelFormat("{value}")
    layer.setAggregateLabelStyle("arialbd.ttf", 8, '0x663300')
    # Set the labels on the x axis.
    c.xAxis().setLabels(labels).setFontAngle(45)

    # Show the same scale on the left and right y-axes
    c.syncYAxis()

    # Set the left y-axis and right y-axis title using 10pt Arial Bold font
    c.yAxis().setTitle("PR Number", "arialbd.ttf",10)
    c.yAxis2().setTitle("PR Number", "arialbd.ttf",10)
    c.yAxis().setMinTickInc(1)
    c.yAxis2().setMinTickInc(1)
    # Set y-axes to transparent
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)

    # Disable ticks on the x-axis by setting the tick color to transparent
    c.xAxis().setTickColor(Transparent)

    # Set the label styles of all axes to 8pt Arial Bold font
    c.xAxis().setLabelStyle("arialbd.ttf", 8).setFontAngle(55)
    c.yAxis().setLabelStyle("arialbd.ttf", 10)
    c.yAxis2().setLabelStyle("arialbd.ttf", 10)

    # Output the chart
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    c.makeChart("/homes/%s/public_html/%s/%s.png" % (user,version[0],name))

def multicylinder(all_list,all_closed_list,all_open_list,end_date_list,title,title2,version,name):
    # Data for the chart
    data0 = all_list
    data1 = all_closed_list
    data2 = all_open_list
    labels = end_date_list 
    data3=[]
    for i in range(len(labels)):
        if data1[i]!=1.7E+308 and data0[i]!=1.7E+308:
            if data0[i]==0:
                data3.append(100)
            else:
                data3.append((data1[i]/data0[i])*100)
        else:
            data3.append(1.7E+308)
    for i in range(len(labels)):
        if data0[i]==1.7E+308:
            if i==0:
                max_data0=80
            else:
                max_data0=data0[i-1]
            break
    for i in range(len(labels)):
        if data1[i]!=1.7E+308 and data0[i]!=1.7E+308:
            if i==len(labels)-1:
                max_data0=data0[i]
    scaleFactor = max_data0/80
    if scaleFactor == 0 :
        # Avoid division by zero error for zero data
        scaleFactor = 1

    # Create a XYChart object of size 600 x 320 pixels, with a light grey (eeeeee)
    # background, black border, 1 pixel 3D border effect and rounded corners.
    
    if len(end_date_list)>11:
        c = XYChart(1200, 320, brushedSilverColor(), Transparent, 2)
    else:
        c = XYChart(600, 320, brushedSilverColor(), Transparent, 2)    
    c.setRoundedFrame()
    c.setDropShadow()

    # Add a title to the chart using 14 pts Arial Bold Italic font
    title = c.addTitle("%s" % title, "timesbi.ttf", 15,'0xffffff')
    title.setBackground('0x0000cc', '0x000000', glassEffect(ReducedGlare))
    #timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    if len(end_date_list)>11:
        timeStamp = c.addText(1170, 318, "%s" % title2, "arialbd.ttf")
    else:
        timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    timeStamp.setAlignment(BottomRight)

    # Set the plotarea at (50, 50) and of 500 x 200 pixels in size. Use alternating light
    # grey (f8f8f8) / white (ffffff) background. Set border to transparent and use grey
    # (CCCCCC) dotted lines as horizontal and vertical grid lines
    #c.setPlotArea(70, 55, 1050, 200, '0xffffff', '0xf8f8f8', Transparent, c.dashLineColor(
    #    '0xcccccc', DotLine), c.dashLineColor('0xcccccc', DotLine))
  
    c.setPlotArea(70, 55, 1050, 200, -1, -1, Transparent)
    # Add a legend box at (50, 22) using horizontal layout. Use 10 pt Arial Bold Italic
    # font, with transparent background
    legendBox = c.addLegend(c.getWidth() / 2, title.getHeight(), 0, "arialbd.ttf", 10)
    legendBox.setAlignment(TopCenter)
    legendBox.setBackground(Transparent, Transparent)
    # Set the x axis labels
    c.xAxis().setLabels(labels)
    c.xAxis().setLabelStyle("arialbd.ttf", 8).setFontAngle(45)
    c.yAxis().setLabelStyle("arialbd.ttf", 8)
    c.yAxis2().setLabelStyle("arialbd.ttf", 8)
    # Draw the ticks between label positions (instead of at label positions)
    c.xAxis().setTickOffset(0.5)
    #c.syncYAxis()
    # Add axis title
    c.yAxis2().setTitle("PR Number", "arialbd.ttf",10)
    c.yAxis().setTitle("Closed Rate (%)", "arialbd.ttf",10)
    c.yAxis2().setMinTickInc(1)
    #c.yAxis().setMinTickInc(1)
    c.yAxis2().setColors(Transparent)
    c.yAxis().setColors(Transparent)

    c.yAxis().setLinearScale(0, 100, 20)

    # Set the format of the secondary (right) y-axis label to include a percentage sign
    c.yAxis().setLabelFormat("{value}%")

    # Set the relationship between the two y-axes, which only differ by a scaling factor
    c.yAxis2().syncAxis(c.yAxis(), scaleFactor)

    # Set the format of the primary y-axis label foramt to show no decimal point
    c.yAxis2().setLabelFormat("{value|0}")

    # Set axis line width to 2 pixels
    c.xAxis().setWidth(2)
    c.yAxis2().setWidth(2)
    c.yAxis().setWidth(2)
    c.xAxis().setMargin(15, 15)
    # Add a line layer for the pareto line
    lineLayer = c.addLineLayer2()

    # Add the pareto line using deep blue (0000ff) as the color, with circle symbols
    lineLayer.addDataSet(data3, '0x0000ff',"Closed Rate").setDataSymbol(GlassSphere2Shape, 9)

    # Set the line width to 2 pixel
    lineLayer.setLineWidth(2)

    # Bind the line layer to the secondary (right) y-axis.

    # Add a multi-bar layer with 3 data sets
    layer = c.addBarLayer2(Side)
    layer.setBorderColor(Transparent, softLighting(Right))
    layer.addDataSet(data0, '0xff6600', "Total PRs")
    if len(end_date_list)<=21 and max_data0<100: 
        layer.setAggregateLabelFormat("{value}")
        layer.setAggregateLabelStyle("arialbd.ttf", 8, '0x663300')
    if len(end_date_list)<=21 and max_data0>=100: 
        layer.setAggregateLabelFormat("{value}")
        layer.setAggregateLabelStyle("arial.ttf", 5, '0x663300')
    layer.addDataSet(data1, '0x66aaee', "Closed PRs")
    layer.addDataSet(data2, '0xeebb22', "Open PRs")
    # Set bar shape to circular (cylinder)
    layer.setBarShape(CircleShape)
    layer.setUseYAxis2()
    # Configure the bars within a group to touch each others (no gap)
    layer.setBarGap(0.2, TouchBar)
    c.packPlotArea(15, legendBox.getTopY() + legendBox.getHeight()+30, c.getWidth() - 16,
    c.getHeight() - 20)
    # Output the chart
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    c.makeChart("/homes/%s/public_html/%s/%s.png" % (user,version[0],name))

def multicylinder_weekly(all_list,total_list,closed_list,open_list,end_date_list,title,title2,version,name):
    # Data for the chart
    data0 = total_list
    data1 = closed_list
    data2 = open_list
    labels = end_date_list 
    data3= all_list
    max_list=[]
    for i in range(len(labels)):
        if data0[i]==1.7E+308:
            if i==0:
                max_data0=100
            else:
                max_data0=data0[i-1]
            break
    for i in range(len(labels)):
        if data0[i]!=1.7E+308:
            max_list.append(data0[i])
    max_data0=max(max_list)
    for i in range(len(labels)):
        if data3[i]==1.7E+308:
            if i==0:
                max_data3=100
            else:
                max_data3=data3[i-1]
            break
    for i in range(len(labels)):
        if data3[i]!=1.7E+308:
            if i==len(labels)-1:
                max_data3=data3[i]
    if not max_data3==0:
        scaleFactor = max_data0/(max_data3*0.9)
    else:
        scaleFactor = 1
    #scaleFactor = 0.3
    if scaleFactor == 0 :
        # Avoid division by zero error for zero data
        scaleFactor = 1

    # Create a XYChart object of size 600 x 320 pixels, with a light grey (eeeeee)
    # background, black border, 1 pixel 3D border effect and rounded corners.
    
    if len(end_date_list)>11:
        c = XYChart(1200, 320, brushedSilverColor(), Transparent, 2)
    else:
        c = XYChart(600, 320, brushedSilverColor(), Transparent, 2)    
    c.setRoundedFrame()
    c.setDropShadow()

    # Add a title to the chart using 14 pts Arial Bold Italic font
    title = c.addTitle("%s" % title, "timesbi.ttf", 15,'0xffffff')
    title.setBackground('0x0000cc', '0x000000', glassEffect(ReducedGlare))
    #timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    if len(end_date_list)>11:
        timeStamp = c.addText(1170, 318, "%s" % title2, "arialbd.ttf")
    else:
        timeStamp = c.addText(570, 318, "%s" % title2, "arialbd.ttf")
    timeStamp.setAlignment(BottomRight)

    # Set the plotarea at (50, 50) and of 500 x 200 pixels in size. Use alternating light
    # grey (f8f8f8) / white (ffffff) background. Set border to transparent and use grey
    # (CCCCCC) dotted lines as horizontal and vertical grid lines
    #c.setPlotArea(70, 55, 1050, 200, '0xffffff', '0xf8f8f8', Transparent, c.dashLineColor(
    #    '0xcccccc', DotLine), c.dashLineColor('0xcccccc', DotLine))
  
    c.setPlotArea(70, 55, 1050, 200, -1, -1, Transparent)
    # Add a legend box at (50, 22) using horizontal layout. Use 10 pt Arial Bold Italic
    # font, with transparent background
    legendBox = c.addLegend(c.getWidth() / 2, title.getHeight(), 0, "arialbd.ttf", 10)
    legendBox.setAlignment(TopCenter)
    legendBox.setBackground(Transparent, Transparent)
    # Set the x axis labels
    c.xAxis().setLabels(labels)
    c.xAxis().setLabelStyle("arialbd.ttf", 8).setFontAngle(45)
    c.yAxis().setLabelStyle("arialbd.ttf", 8)
    c.yAxis2().setLabelStyle("arialbd.ttf", 8)
    # Draw the ticks between label positions (instead of at label positions)
    c.xAxis().setTickOffset(0.5)
    #c.syncYAxis()
    # Add axis title
    c.yAxis2().setTitle("Weekly PRs Number", "arialbd.ttf",10)
    c.yAxis().setTitle("Total PRs Number", "arialbd.ttf",10)
    c.yAxis2().setMinTickInc(1)
    #c.yAxis().setMinTickInc(1)
    c.yAxis().setColors(Transparent)
    c.yAxis2().setColors(Transparent)

    #c.yAxis2().setLinearScale(0, 100, 20)

    # Set the format of the secondary (right) y-axis label to include a percentage sign
    c.yAxis().setLabelFormat("{value|0}")

    # Set the relationship between the two y-axes, which only differ by a scaling factor
    c.yAxis2().syncAxis(c.yAxis(), scaleFactor)

    # Set the format of the primary y-axis label foramt to show no decimal point
    c.yAxis2().setLabelFormat("{value|0}")

    # Set axis line width to 2 pixels
    c.xAxis().setWidth(2)
    c.yAxis2().setWidth(2)
    c.yAxis().setWidth(2)
    c.xAxis().setMargin(15, 15)
    
    # Add a line layer for the pareto line
    lineLayer = c.addLineLayer2()

    # Add the pareto line using deep blue (0000ff) as the color, with circle symbols
    lineLayer.addDataSet(data3, '0x0000ff',"Total PRs").setDataSymbol(GlassSphere2Shape, 9)

    # Set the line width to 2 pixel
    lineLayer.setLineWidth(2)

    # Bind the line layer to the secondary (right) y-axis.
    #lineLayer.setUseYAxis2()

    # Add a multi-bar layer with 3 data sets
    layer = c.addBarLayer2(Side)
    layer.setBorderColor(Transparent, softLighting(Right))
    layer.addDataSet(data0, '0xff6600', "Arrived PRs")
    if len(end_date_list)<=21 and max_data0<100: 
        layer.setAggregateLabelFormat("{value}")
        layer.setAggregateLabelStyle("arialbd.ttf", 8, '0x663300')
    if len(end_date_list)<=21 and max_data0>=100: 
        layer.setAggregateLabelFormat("{value}")
        layer.setAggregateLabelStyle("arial.ttf", 5, '0x663300')
    layer.addDataSet(data1, '0x66aaee', "Closed PRs")
    layer.addDataSet(data2, '0xeebb22', "Open PRs")
    layer.setUseYAxis2()
    # Set bar shape to circular (cylinder)
    layer.setBarShape(CircleShape)
    
    

    # Configure the bars within a group to touch each others (no gap)
    layer.setBarGap(0.2, TouchBar)
    c.packPlotArea(15, legendBox.getTopY() + legendBox.getHeight()+30, c.getWidth() - 16,
    c.getHeight() - 20)
    
    # Output the chart
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    c.makeChart("/homes/%s/public_html/%s/%s.png" % (user,version[0],name))

def write_HTML(prList,version,title2,name):
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    htmlfile=open('/homes/%s/public_html/%s/%s.html' % (user,version[0],name), 'w')   
    htmlfile.write("""<html><head><title>%s</title>
</head>
%s records // generated at %s <br /><br />
<table id="records" class="tablesorter">
<thead>
<tr>

<th align="left" id="number" class="header headerSortDown">Number</th>

<th align="left" id="synopsis" class="header">Synopsis</th>

<th align="left" id="reported-in" class="header">Reported-In</th>

<th align="left" id="submitter-id" class="header">Submitter-Id</th>

<th align="left" id="product" class="header">Product</th>

<th align="left" id="category" class="header">Category</th>

<th align="left" id="problem-level" class="header">Problem-Level</th>

<th align="left" id="blocker" class="header">Blocker</th>

<th align="left" id="planned-release" class="header">Planned-Release</th>

<th align="left" id="state" class="header">State</th>

<th align="left" id="responsible" class="header">Responsible</th>

<th align="left" id="originator" class="header">Originator</th>

<th align="left" id="arrival-date" class="header">Arrival-Date</th>
</tr>
</thead>
<tbody>""" % (title2,str(len(prList)),commands.getstatusoutput('date')[1]))

    for i in range(len(prList)):
        if (i%2==1):
            class_option='odd'
        else:
            class_option='even'
        htmlfile.write("""<tr class="%s">
<td>

<span class="nowrap"><a href="https://gnats.juniper.net/web/default/%s">%s</a> <a href="https://gnats.juniper.net/web/default/%s/edit" class="noprint">edit</a></span></td>
<td>
%s</td>
<td>
%s</td>
<td>
%s</td>
<td>
srx-series</td>
<td>

<a href="https://gnats.juniper.net/web/default/do-query?category=%s&ignoreclosed=on&columns=synopsis&columns=reported-in&columns=submitter-id&columns=product&columns=category&columns=severity&columns=priority&columns=blocker&columns=planned-release&columns=state&columns=responsible&columns=originator&columns=arrival-date">%s</a></td>
<td>
%s</td>
<td>
%s</td>
<td>
%s</td>
<td>
%s</td>
<td>

<a href="mailto:%s@juniper.net">%s</a></td>
<td>

<a href="mailto:%s@juniper.net">%s</a></td>
<td>
%s</td>
</tr>""" % (class_option,prList[i][0],prList[i][0],prList[i][0],prList[i][1],prList[i][2],prList[i][3],prList[i][5],prList[i][5],prList[i][6],prList[i][8],prList[i][9],prList[i][10],prList[i][11],prList[i][11],prList[i][12],prList[i][12],prList[i][14]))

    htmlfile.write("""</tr></tbody>
</table><br />
</body></html>""")
    htmlfile.close()

def write_index(expr,version,title2,all_prList,open_prList,info_feedback_prList,blocker_prList,unclosed_blocker_prList,open_lifetime_prList,info_lifetime_prList,feedback_lifetime_prList,info_feedback_lifetime_prList,rate_width,trend_width,category_width,user_width):
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    if not os.path.exists('/homes/%s/public_html/%s' % (user,version[0])):
        os.mkdir('/homes/%s/public_html/%s' % (user,version[0]))
    htmlfile=open('/homes/%s/public_html/%s/index.html' % (user,version[0]), 'w')   
    htmlfile.write("""<html><body><head><title>%s</title>
</head>""" % title2)
    htmlfile.write("""<p style="text-align: center;"><a href="http://www-in.juniper.net/~%s/%s/all.html"><font color="#0066FF">All PRs (%s records)<font></a>""" % (user,version[0],str(len(all_prList))))
    htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/open.html"><font color="#009900">Open PRs (%s records)<font></a>""" % (user,version[0],str(len(open_prList))))
    htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/info_feedback.html"><font color="#FF0000">Info and Feedback PRs (%s records)<font></a>""" % (user,version[0],str(len(info_feedback_prList))))
    htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/blocker.html"><font color="#FF0000">Blocker PRs (%s records)<font></a>""" % (user,version[0],str(len(blocker_prList))))
    htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/unclosed_blocker.html"><font color="#FF0000">Unclosed Blocker PRs (%s records)<font></a></p>""" % (user,version[0],str(len(unclosed_blocker_prList))))
    htmlfile.write('\n')
    
    
    htmlfile.write("""<p style="text-align: left;"><font color="#0066FF">PR in specified state more than 3 days:<font></p>""")
    #htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write('\n')
    htmlfile.write("""<p style="text-align: center;"><a href="http://www-in.juniper.net/~%s/%s/open_lifetime.html"><font color="#009900">Open PRs (%s records)<font></a>""" % (user,version[0],str(len(open_lifetime_prList))))
    htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/info_lifetime.html"><font color="#FF0000">Info PRs (%s records)<font></a>""" % (user,version[0],str(len(info_lifetime_prList))))
    htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/feedback.html"><font color="#FF0000">Feedback PRs (%s records)<font></a>""" % (user,version[0],str(len(feedback_lifetime_prList))))
    htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/info_feedback_lifetime.html"><font color="#FF0000">Info and Feedback PRs (%s records)<font></a></p>""" % (user,version[0],str(len(info_feedback_lifetime_prList))))
    htmlfile.write('\n')
    #htmlfile.write("""<p style="text-align: left;"><font color="#0066FF">GNATS PR Query Expression:<font></p>""")
    #htmlfile.write("""<p style="text-align: left;"><font color="#0066FF">%s<font></p>""" % expr)
    htmlfile.write("""<table width="100%" border="1" bordercolor="#000000">
   <tr bordercolor="#FFFFFF">""")
    htmlfile.write("""<td><p style="text-align: left;"><font color="#0066FF">GNATS PR Query Expression: %s<font></p></td>""" % expr)
    htmlfile.write("""
   </tr>
</table>
<p>""")
    htmlfile.write("""
    <table width="100%" border="0" bordercolor="#000000">
   <tr>
     <td>PR State Mapping Table:</td>
   </tr>
</table>
    <table width="100%" border="0" cellspacing="1" bgcolor="#000000">
   <tr>
     <td bgcolor="#FFFFFF">Info</td>
     <td bgcolor="#FFFFFF">need-info; need-setup; try-fix</td>
   </tr>
   <tr>
     <td bgcolor="#FFFFFF">Analyzed</td>
     <td bgcolor="#FFFFFF">under-analysis; under-review; awaiting-build; ready-to-commit</td>
   </tr>
     <td bgcolor="#FFFFFF">Feedback</td>
     <td bgcolor="#FFFFFF">verify-resolution</td>
   </tr>
</table>""")
    #htmlfile.write('&nbsp;&nbsp;')
    htmlfile.write("""<center>
<a href="http://www-in.juniper.net/~%s/%s/search_pr.html"><img src="state.png" width="600" height="320" /></a>
<a href="http://www-in.juniper.net/~%s/%s/search_pr.log"><img src="stackedbar_responsible.png" width="%s" height="320" /></a>
<img src="closed_rate.png" width="%s" height="320" />
<img src="weekly_arrived.png" width="%s" height="320" />
<img src="total_trend.png" width="%s" height="320" />
<img src="weekly_trend.png" width="%s" height="320" />
<img src="category_all.png" width="%s" height="320" />
<img src="class.png" width="600" height="320" />
<img src="platform.png" width="600" height="320" />
<img src="attributes.png" width="600" height="320" />
<img src="blocker.png" width="600" height="320" />
<img src="problem_level.png" width="600" height="320" />  
<img src="category.png" width="600" height="320" />
</center>
</body>
</html>""" % (user,version[0],user,version[0],user_width,rate_width,rate_width,trend_width,trend_width,category_width))
    htmlfile.close()

def write_search_pr_html(version,title2,all_prList,open_prList,info_feedback_prList,blocker_prList,unclosed_blocker_prList):
    user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
    if not os.path.exists('/homes/%s/public_html/%s' % (user,version[0])):
        os.mkdir('/homes/%s/public_html/%s' % (user,version[0]))
    htmlfile=open('/homes/%s/public_html/%s/search_pr.html' % (user,version[0]), 'w')   
    htmlfile.write("""<html><body><head><title>%s</title>
</head>""" % title2)
    htmlfile.write("""<p style="text-align: center;"><a href="http://www-in.juniper.net/~%s/%s/all.html"><font color="#0066FF">All PRs (%s records)<font></a><br>""" % (user,version[0],str(len(all_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/closed.html"><font color="#009900">Closed PRs (%s records)<font></a><br>""" % (user,version[0],str(len(closed_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/open.html"><font color="#009900">Open PRs (%s records)<font></a><br>""" % (user,version[0],str(len(open_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/info.html"><font color="#009900">Info PRs (%s records)<font></a><br>""" % (user,version[0],str(len(info_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/feedback.html"><font color="#009900">Feedback PRs (%s records)<font></a><br>""" % (user,version[0],str(len(feedback_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/monitored.html"><font color="#009900">Monitored PRs (%s records)<font></a><br>""" % (user,version[0],str(len(monitored_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/analyzed.html"><font color="#009900">Analyzed PRs (%s records)<font></a><br>""" % (user,version[0],str(len(analyzed_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/assigned.html"><font color="#009900">Assigned PRs (%s records)<font></a><br>""" % (user,version[0],str(len(assigned_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/info_feedback.html"><font color="#FF0000">Info and Feedback PRs (%s records)<font></a><br>""" % (user,version[0],str(len(info_feedback_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/info_feedback_monitored.html"><font color="#FF0000">Info Feedback and Monitored PRs (%s records)<font></a><br>""" % (user,version[0],str(len(info_feedback_monitored_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/blocker.html"><font color="#009900">Blocker PRs (%s records)<font></a><br>""" % (user,version[0],str(len(blocker_prList))))
    htmlfile.write('\n')
    htmlfile.write("""<a href="http://www-in.juniper.net/~%s/%s/unclosed_blocker.html"><font color="#FF0000">Unclosed Blocker PRs (%s records)<font></a></p>""" % (user,version[0],str(len(unclosed_blocker_prList))))
    htmlfile.write("""</body>
</html>""")
    htmlfile.close()

def state_count(data,data_state,state_list):
    month = {"Jan"  : '01',
                 "Feb"  : '02',
                 "Mar"  : '03',
                 "Apr"  : '04',
                 "May"  : '05',
                 "Jun"  : '06',
                 "Jul"  : '07',
                 "Aug"  : '08',
                 "Sep"  : '09',
                 "Oct"  : '10',
                 "Nov"  : '11',
                 "Dec"  : '12',             
                 }
    names=locals()
    timeline_list=[]
    for item in data_state[1]:
        timeline=[]
        for temp in item:
            if re.search(r'\sState\{1\}', temp):
                #print temp
                item_list=re.split('\s+',temp)
                #time_in_second=get_time(item_list[:6])
                time_in_date="%s %s %s %s" % (item_list[5],item_list[1],item_list[2],item_list[3]) 
                time_state=[time_in_date]+item_list[7:]
                timeline.append(time_state)
        timeline_list.append(timeline[-1])
    #print timeline_list
    state_time_list=[]
    item_list=re.split('\s+',commands.getstatusoutput('date')[1])
    current_time="%s %s %s %s" % (item_list[5],item_list[1],item_list[2],item_list[3])
    for item in timeline_list:
        state_time=[]
        if len(item)==1:
            state_time.append("%s,%s,%s" % (item[0][1],item[0][0],current_time))
        else:
            for i in range(len(item)):
                if i!=len(item)-1:
                    state_time.append("%s,%s,%s" % (item[i+1][1],item[i][0],item[i+1][0]))
                else:
                    state_time.append("%s,%s,%s" % (item[i][2],item[i][0],current_time))
        state_time_list.append(state_time)
    names['%s_PR_lifetime_list' % '_'.join(state_list)]=[]
    for i in range(len(state_time_list)):
        if re.split(',',state_time_list[i][-1])[0] in state_list:
            start_time=re.split('\s+',re.split(',',state_time_list[i][-1])[1])
            end_time=re.split('\s+',re.split(',',state_time_list[i][-1])[2])
            start_time_list=[int(start_time[0]),int(month[start_time[1]]),int(start_time[2]),int(re.split(':',start_time[3])[0]),int(re.split(':',start_time[3])[1]),int(re.split(':',start_time[3])[2]),0,0,0]
            end_time_list=[int(end_time[0]),int(month[end_time[1]]),int(end_time[2]),int(re.split(':',end_time[3])[0]),int(re.split(':',end_time[3])[1]),int(re.split(':',end_time[3])[2]),0,0,0]
            start_time_number=time.mktime(start_time_list)
            end_time_number=time.mktime(end_time_list)
            if (end_time_number-start_time_number)>=(86400*3):
                names['%s_PR_lifetime_list' % '_'.join(state_list)].append(data[1][i])
    return names['%s_PR_lifetime_list' % '_'.join(state_list)]

if __name__ == "__main__":
    names=locals()
    title_name='SBU PDT'
    originator='all'
    duration=16
    synopsis='' 
    keyword=''
    expr=''
    data_user=[]
    set_start_date=''
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvs:o:w:k:d:t:e:a:", ["help", "version","synopsis=","originator=","weeks=","keyword=","dir=","title=","expr=","arrived-after="])
    except getopt.GetoptError: 
        usage()
        sys.exit(2)
    for opt, arg in opts:                
        if opt in ("-h", "--help"):      
            usage()
            example()
            print       
            sys.exit()                  
        elif opt in ("-v", "--version"):                
            print 'Version 1.8'
            sys.exit()
        elif opt in ("-s", "--synopsis"):                
            synopsis=arg
            #query_option='synopsis'
            if re.match(r'.*?\d+\.\d+.*?', synopsis):
                p1 = re.compile('.*?(\d+\.\d+).*?')
            else:
                p1 = re.compile('.*?(\d+).*?')
            version = p1.findall(synopsis)
        elif opt in ("-o", "--originator"):                
            originator=arg     
        elif opt in ("-w", "--weeks"):                
            duration=arg  
        elif opt in ("-k", "--keyword"):                
            keyword=arg  
            #query_option='keyword'
            p1 = re.compile('.*?(\d+\.\d+).*?')
            version = p1.findall(keyword)
        elif opt in ("-d", "--dir"):                
            version = [arg]
        elif opt in ("-t", "--title"):                
            title_name = arg
        elif opt in ("-e", "--expr"):                
            expr = arg
        elif opt in ("-a", "--arrived-after"):                
            set_start_date = arg
        else:   
            usage()   
            sys.exit()
    if len(sys.argv) < 2:   
        usage()  
        #print
        #example() 
        sys.exit() 
    else:   
            userlist=[]
            data=query_PR_all(synopsis,keyword,expr)
            data_state=query_PR_state_all(expr)
            #print data
            #print data_state
            state_list=['open']
            names['%s_lifetime_prList' % '_'.join(state_list)]=state_count(data,data_state,state_list)
            state_list_new=['need-info']
            state_list=['info']
            names['%s_lifetime_prList' % '_'.join(state_list)]=state_count(data,data_state,state_list_new)
            state_list_new=['awaiting-build','verify-resolution']
            state_list=['feedback']
            names['%s_lifetime_prList' % '_'.join(state_list)]=state_count(data,data_state,state_list_new)
            state_list_new=['need-info','awaiting-build','verify-resolution']
            state_list=['info','feedback']
            names['%s_lifetime_prList' % '_'.join(state_list)]=state_count(data,data_state,state_list_new)
            pr_numberList=[]
            for i in range(int(data[0][0][1])):
                pr_numberList.append(data[1][i][0])
            #print "\n"
            #print "pr_list=%s" % pr_numberList
            if originator=='all': 
                #print data
                #print len(data[1])
                originatorList=[]
                for i in range(int(data[0][0][1])):
                    originatorList.append(data[1][i][12])
                checked=[]
                totalNumber=len(originatorList)
                for item in originatorList:
                    if item not in checked:
                        checked.append(item)
                originatorDirectory={}
                for item in checked:
                    originatorDirectory[item]= '0'
                for item in originatorList:
                    for key, value in originatorDirectory.items():
                        if re.match(r'%s' % key, item):
                            count=int(originatorDirectory[key])
                            count+=1
                            originatorDirectory[key]=count
                dataList=sorted(originatorDirectory.iteritems(), key=lambda d:d[1], reverse = True )
                for i in range(len(dataList)):
                    userlist.append(dataList[i][0])
            else:
                teamlist=originator.split(',')
                for item in teamlist:
                    #if re.match(r'\w+-team', item):
                    if re.search(r'-team$', item):
                        if len(item.split('-'))==2:
                            team_name=item.split('-')[0]
                        else:
                            team_name='_'.join(item.split('-')[0:-1])
                        if not team_name in team_list:
                            print "Invalid team name, please check the team name"
                            sys.exit()
                        else:
                            userlist+=names['%s_team' % team_name]
                    else:
                        userlist.append(item)                
                for i in range(int(data[0][0][1])):
                    if data[1][i][12] in userlist:
                        data_user.append(data[1][i])
                results=[]
                results.append([str(len(data_user)),str(len(data_user)),commands.getstatusoutput('date')[1]]) 
                data=[results,data_user]
            for user in userlist:
                names['%s_list' % user]=[]
                for i in range(int(data[0][0][1])):
                    if user==data[1][i][12]:
                        names['%s_list' % user].append(data[1][i]) 
            totalPR=0
            totalList = {"open"   : '0',
                         "info"  : '0',
                         "analyzed"  : '0',
                         "assigned"  : '0',
                         "feedback"  : '0',
                         "monitored"  : '0',
                         "closed"  : '0',
                          }
            totalList1 = {"3-IL1"   : '0',
                          "4-IL2"  : '0',
                          "5-IL3"  : '0',
                          "6-IL4"  : '0',
                          "1-CL1"  : '0',
                          "2-CL2"  : '0',
                          "4-CL3"  : '0',
                          "5-CL4"  : '0',
                           }
            totalList2 = {"3-IL1"   : '0',
                          "4-IL2"  : '0',
                          "5-IL3"  : '0',
                          "6-IL4"  : '0',
                          "1-CL1"  : '0',
                          "2-CL2"  : '0',
                          "4-CL3"  : '0',
                          "5-CL4"  : '0',
                           }
            for key, value in totalList.items():
                names['total_%s' % key]=0
            for key, value in totalList1.items():
                problem_level='_'.join(key.split('-'))
                names['total_%s' % problem_level]=0
            for key, value in totalList2.items():
                problem_level='_'.join(key.split('-'))
                names['total_%s' % problem_level]=0
            infoList=[]
            feedbackList=[]
            openList=[]
            closedList=[]
            monitoredList=[]
            assignedList=[]
            analyzedList=[]
            categoryList=[]
            platformList=[]
            blockerList=[]
            classList=[]
            attributesList=[]
            info_feedback_prList=[]
            open_prList=[]
            closed_prList=[]
            info_prList=[]
            feedback_prList=[]
            monitored_prList=[]
            analyzed_prList=[]
            assigned_prList=[]
            IL1_prList=[]
            blocker_prList=[]
            unclosed_blocker_prList=[]
            all_prList=[]
            #p1 = re.compile('.*?(\d+\.\d+).*?')
            #version = p1.findall(synopsis)
            title2= 'JUNOS %s statistics at %s' % (version[0],commands.getstatusoutput('date')[1])
            user=commands.getstatusoutput("who am i")[1].split('tty')[0].rstrip()
            if not os.path.exists('/homes/%s/public_html/%s' % (user,version[0])):
                os.mkdir('/homes/%s/public_html/%s' % (user,version[0]))
            logfile=open('/homes/%s/public_html/%s/search_pr.log' % (user,version[0]), 'w')
            logfile.write('%s\n' % title2)
            logfile.write("="*149)
            logfile.write('\nTotal    Open    Info    Analyzed     Assigned    Feedback    Monitored    Closed    Originator            IL1    IL2    IL3    IL4    Weighted_Total\n')
            logfile.write("="*149)
            logfile.write("\n")
            print
            print ('%s' % title2)
            print "="*149
            print ("Total    Open    Info    Analyzed     Assigned    Feedback    Monitored    Closed    Originator            IL1    IL2    IL3    IL4    Weighted_Total")
            print "="*149
            for originator in userlist:
                stateList = {"open"   : '0',
                             "info"  : '0',
                             "analyzed"  : '0',
                             "assigned"  : '0',
                             "feedback"  : '0',
                             "monitored"  : '0',
                             "closed"  : '0',
                              }
                new_state_List = {"open"   : 'open',
                             "info"  : 'need-info_need-setup_try-fix',
                             "analyzed"  : 'under-analysis_under-review',
                             "assigned"  : 'assigned',
                             "feedback"  : 'awaiting-build_verify-resolution_ready-to-commit',
                             "monitored"  : 'monitored',
                             "closed"  : 'closed',
                              }
                severityList = {"3-IL1"   : '0',
                                "4-IL2"  : '0',
                                "5-IL3"  : '0',
                                "6-IL4"  : '0',
                                "1-CL1"  : '0',
                                "2-CL2"  : '0',
                                "4-CL3"  : '0',
                                "5-CL4"  : '0',
                                 }
                priorityList = {"3-IL1"   : '0',
                                "4-IL2"  : '0',
                                "5-IL3"  : '0',
                                "6-IL4"  : '0',
                                "1-CL1"  : '0',
                                "2-CL2"  : '0',
                                "4-CL3"  : '0',
                                "5-CL4"  : '0',
                                 }
                if not names['%s_list' % originator]:
                    results=[]
                    results.append([str(0),str(0),commands.getstatusoutput('date')[1]]) 
                    user_data=[results,names['%s_list' % originator]]
                else:
                    results=[]
                    results.append([str(len(names['%s_list' % originator])),str(len(names['%s_list' % originator])),commands.getstatusoutput('date')[1]]) 
                    user_data=[results,names['%s_list' % originator]]
                #print user_data
                #print
                totalPR+=int(user_data[0][0][1])
                for i in range(int(user_data[0][0][1])):
                    categoryList.append(user_data[1][i][5])
                    platformList.append(user_data[1][i][4])
                    blockerList.append(user_data[1][i][8])
                    attributesList.append(user_data[1][i][13])
                    classList.append(user_data[1][i][15])
                    all_prList.append(user_data[1][i])
                    if user_data[1][i][10] in ['need-info','awaiting-build','verify-resolution']:
                        info_feedback_prList.append(user_data[1][i])
                    if user_data[1][i][10] in ['open']:
                        open_prList.append(user_data[1][i])
                    if user_data[1][i][10] in ['closed']:
                        closed_prList.append(user_data[1][i])
                    if user_data[1][i][10] in ['need-info','need-setup','try-fix']:
                        info_prList.append(user_data[1][i])
                    if user_data[1][i][10] in ['awaiting-build','verify-resolution','ready-to-commit']:
                        feedback_prList.append(user_data[1][i])
                    if user_data[1][i][10] in ['monitored']:
                        monitored_prList.append(user_data[1][i])
                    if user_data[1][i][10] in ['under-analysis','under-review']:
                        analyzed_prList.append(user_data[1][i])
                    if user_data[1][i][10] in ['assigned']:
                        assigned_prList.append(user_data[1][i])
                    if user_data[1][i][8]:
                        blocker_prList.append(user_data[1][i])
                        if not user_data[1][i][10] in ['closed']:
                            unclosed_blocker_prList.append(user_data[1][i])
                    for key, value in stateList.items():
                        if key in ['feedback','info']:
                            if re.match(r'%s' % new_state_List[key].split('_')[0], user_data[1][i][10]) or re.match(r'%s' % new_state_List[key].split('_')[1], user_data[1][i][10]) or re.match(r'%s' % new_state_List[key].split('_')[2], user_data[1][i][10]):
                                count=int(stateList[key])
                                count+=1
                                stateList[key]=str(count)
                        elif key in ['analyzed']:
                            if re.match(r'%s' % new_state_List[key].split('_')[0], user_data[1][i][10]) or re.match(r'%s' % new_state_List[key].split('_')[1], user_data[1][i][10]):
                                count=int(stateList[key])
                                count+=1
                                stateList[key]=str(count)
                        else:
                            if re.match(r'%s' % new_state_List[key], user_data[1][i][10]):
                                count=int(stateList[key])
                                count+=1
                                stateList[key]=str(count)
                    for key, value in severityList.items():
                        if re.match(r'%s' % key, user_data[1][i][6]):
                            count=int(severityList[key])
                            count+=1
                            severityList[key]=str(count)
                    for key, value in priorityList.items():
                        if re.match(r'%s' % key, user_data[1][i][7]):
                            count=int(priorityList[key])
                            count+=1
                            priorityList[key]=str(count)  
                weighted_total=4*int(severityList['3-IL1']) + 3*int(severityList['4-IL2']) + 2*int(severityList['5-IL3']) + 1*int(severityList['6-IL4'])
                logfile.write("%5.5s%8.5s%8.5s%12.5s%13.5s%12.5s%13.5s%10.5s    %-20.20s%5.5s%7.5s%7.5s%7.5s%18.5s\n" % (user_data[0][0][1],stateList['open'],stateList['info'],stateList['analyzed'],stateList['assigned'],stateList['feedback'],stateList['monitored'],stateList['closed'],originator,severityList['3-IL1'],severityList['4-IL2'],severityList['5-IL3'],severityList['6-IL4'],str(weighted_total)))
                print ("%5.5s%8.5s%8.5s%12.5s%13.5s%12.5s%13.5s%10.5s    %-20.20s%5.5s%7.5s%7.5s%7.5s%18.5s" % (user_data[0][0][1],stateList['open'],stateList['info'],stateList['analyzed'],stateList['assigned'],stateList['feedback'],stateList['monitored'],stateList['closed'],originator,severityList['3-IL1'],severityList['4-IL2'],severityList['5-IL3'],severityList['6-IL4'],str(weighted_total)))
                infoList.append(int(stateList['info']))
                feedbackList.append(int(stateList['feedback']))
                openList.append(int(stateList['open']))
                closedList.append(int(stateList['closed']))
                monitoredList.append(int(stateList['monitored']))
                assignedList.append(int(stateList['assigned']))
                analyzedList.append(int(stateList['analyzed']))
                for key, value in stateList.items():
                    names['total_%s' % key]+=int(stateList[key])
                for key, value in severityList.items():
                    problem_level='_'.join(key.split('-'))
                    names['total_%s' % problem_level]+=int(severityList[key])
            for key, value in totalList.items():
                names['total_%s' % key]=str(names['total_%s' % key])
            for key, value in totalList1.items():
                problem_level='_'.join(key.split('-'))
                names['total_%s' % problem_level]=str(names['total_%s' % problem_level])
            totalPR=str(totalPR)
            weight_total_summary=4*int(total_3_IL1)+2*int(total_4_IL2)+2*int(total_5_IL3)+1*int(total_6_IL4)
            print "="*149
            print ("%5.5s%8.5s%8.5s%12.5s%13.5s%12.5s%13.5s%10.5s    Summary        %10.5s%7.5s%7.5s%7.5s%18.5s" % (totalPR,total_open,total_info,total_analyzed,total_assigned,total_feedback,total_monitored,total_closed,total_3_IL1,total_4_IL2,total_5_IL3,total_6_IL4,str(weight_total_summary)))
            print "="*149
            logfile.write("="*149)
            logfile.write("\n%5.5s%8.5s%8.5s%12.5s%13.5s%12.5s%13.5s%10.5s    Summary        %10.5s%7.5s%7.5s%7.5s%18.5s\n" % (totalPR,total_open,total_info,total_analyzed,total_assigned,total_feedback,total_monitored,total_closed,total_3_IL1,total_4_IL2,total_5_IL3,total_6_IL4,str(weight_total_summary)))
            logfile.write("="*149)
            pie_data = [int(total_closed),int(total_open),int(total_info),int(total_feedback),int(total_monitored),int(total_analyzed),int(total_assigned)]
            labels = ["Closed=%s" % total_closed,"Open=%s" % total_open,"Info=%s" % total_info,"Feedback=%s" % total_feedback,"Monitored=%s" % total_monitored,"Analyzed=%s" % total_analyzed,"Assigned=%s" % total_assigned]
            title = '%s PR\'s State Statistics (Total %s PRs)' % (title_name,totalPR)
            #p1 = re.compile('.*?(\d+\.\d+).*?')
            #version = p1.findall(synopsis)
            title2= 'JUNOS %s statistics at %s' % (version[0],data[0][0][2])
            #print pie_data
            #print
            name='state'
            legendPie2(pie_data,labels,title,title2,version,name)
            pie_data = [int(total_3_IL1),int(total_4_IL2),int(total_5_IL3),int(total_6_IL4),int(total_1_CL1),int(total_2_CL2),int(total_4_CL3),int(total_5_CL4)]
            labels = ["3-IL1=%s" % total_3_IL1,"4-IL2=%s" % total_4_IL2,"5-IL3=%s" % total_5_IL3,"6-IL4=%s" % total_6_IL4,"1-CL1=%s" % total_1_CL1,"2-CL2=%s" % total_2_CL2,"4-CL3=%s" % total_4_CL3,"5-CL4=%s" % total_5_CL4]
            title = '%s PR\'s Problem Level Statistics (Total %s PRs)' % (title_name,totalPR)
            #print pie_data
            #print
            name='problem_level'
            legendPie2(pie_data,labels,title,title2,version,name)
            title = '%s Personal Responsible PR\'s State Statistics' % title_name
            valid_infoList=[]
            valid_feedbackList=[]
            valid_monitoredList=[]
            valid_userlist=[]
            for i in range(len(userlist)):
                if not (infoList[i]==0)&(feedbackList[i]==0)&(monitoredList[i]==0):
                     valid_infoList.append(infoList[i])
                     valid_feedbackList.append(feedbackList[i])
                     valid_monitoredList.append(monitoredList[i])
                     valid_userlist.append(userlist[i])
            stackedBar_responsible(valid_infoList,valid_feedbackList,valid_monitoredList,valid_userlist,title,title2,version)
            title = '%s PR\'s State Statistics of Each Originator' % title_name
            #print infoList
            #print 
	    #print feedbackList
            #print
            #print openList
            stackedBar(closedList,openList,infoList,feedbackList,monitoredList,analyzedList,assignedList,userlist,title,title2,version) 
            checked=[]
            for item in categoryList:
                if item not in checked:
                    checked.append(item)
            categoryDirectory={}
            for item in checked:
                categoryDirectory[item]= '0'
            for item in categoryList:
                for key, value in categoryDirectory.items():
                    if re.match(r'^%s$' % key, item):
                        count=int(categoryDirectory[key])
                        count+=1
                        categoryDirectory[key]=count
            dataList=sorted(categoryDirectory.iteritems(), key=lambda d:d[1], reverse = True )
            totalNumber=0
            for i in range(len(dataList)):
                totalNumber+=dataList[i][1]
            toptenNumber=0
            if len(dataList)<=10:
                #for i in range(totalNumber):
                #    toptenNumber+=dataList[i][1]
                #otherNumber=totalNumber-toptenNumber
                pie_data=[]
                labels=[]
                for i in range(len(dataList)):
                    pie_data.append(str(dataList[i][1]))
                    labels.append("%s=%s" % (dataList[i][0],str(dataList[i][1])))
                #pie_data.append(str(otherNumber))
                #labels.append('other=%s' % str(otherNumber))
                title = '%s PR\'s Category Statistics (Total %s PRs)' % (title_name,totalPR)
            else:
                for i in range(10):
                    toptenNumber+=dataList[i][1]
                otherNumber=totalNumber-toptenNumber
                pie_data=[]
                labels=[]
                for i in range(10):
                    pie_data.append(str(dataList[i][1]))
                    labels.append("%s=%s" % (dataList[i][0],str(dataList[i][1])))
                pie_data.append(str(otherNumber))
                labels.append('other=%s' % str(otherNumber))
                title = '%s PR\'s Top Ten Category Statistics (Total %s PRs)' % (title_name,totalPR)
            name='category'
            legendPie2(pie_data,labels,title,title2,version,name)
            bar_data=[]
            labels=[]
            for i in range(len(dataList)):
                bar_data.append(str(dataList[i][1]))
                labels.append("%s" % dataList[i][0])
            if len(labels)>21:
                category_width=1206
            else:
                category_width=600
            title = '%s PR\'s All Category Statistics (Total %s PRs)' % (title_name,totalPR)
            name='category_all'
            cylinderlightbar(bar_data,labels,title,title2,version,name)
            logfile.write("\n")
            logfile.write("="*149)
            logfile.write("\nCategory Statistic:\n")
            logfile.write("="*149)
            logfile.write("\n")
            for i in range(len(dataList)):
                logfile.write("%s.%s=%s\n" % (str(i+1),dataList[i][0],str(dataList[i][1])))
            logfile.write("="*149)
            logfile.close()
            checked=[]
            for i in range(len(platformList)):
                if not platformList[i]:
                    platformList[i]='NotSpecified'
                if re.match(r'.*?:.*?', platformList[i]):
                    platformList[i]=platformList[i].split(':')[0]
            for item in platformList:
                if item not in checked:
                    checked.append(item)
            platformDirectory={}
            for item in checked:
                platformDirectory[item]= '0'
            for item in platformList:
                for key, value in platformDirectory.items():
                    if re.match(r'%s' % key, item):
                        count=int(platformDirectory[key])
                        count+=1
                        platformDirectory[key]=count
            dataList=sorted(platformDirectory.iteritems(), key=lambda d:d[1], reverse = True )
            totalNumber=0
            for i in range(len(dataList)):
                totalNumber+=dataList[i][1]
            toptenNumber=0
            if len(dataList)<=10:
                pie_data=[]
                labels=[]
                for i in range(len(dataList)):
                    pie_data.append(str(dataList[i][1]))
                    labels.append("%s=%s" % (dataList[i][0],str(dataList[i][1])))
                title = '%s PR\'s Platform Statistics (Total %s PRs)' % (title_name,totalPR)
            else:
                for i in range(10):
                    toptenNumber+=dataList[i][1]
                otherNumber=totalNumber-toptenNumber
                pie_data=[]
                labels=[]
                for i in range(10):
                    pie_data.append(str(dataList[i][1]))
                    labels.append("%s=%s" % (dataList[i][0],str(dataList[i][1])))
                pie_data.append(str(otherNumber))
                labels.append('Other=%s' % str(otherNumber))
                title = '%s PR\'s Top Ten Platform Statistics (Total %s PRs)' % (title_name,totalPR)
            name='platform'
            legendPie2(pie_data,labels,title,title2,version,name)
            checked=[]
            for i in range(len(attributesList)):
                if not attributesList[i]:
                    attributesList[i]='no attributes'
            for item in attributesList:
                if item not in checked:
                    checked.append(item)
            attributesDirectory={}
            for item in checked:
                attributesDirectory[item]= '0'
            for item in attributesList:
                for key, value in attributesDirectory.items():
                    if re.match(r'^%s$' % key, item):
                        count=int(attributesDirectory[key])
                        count+=1
                        attributesDirectory[key]=count
            dataList=sorted(attributesDirectory.iteritems(), key=lambda d:d[1], reverse = True )
            totalNumber=0
            for i in range(len(dataList)):
                totalNumber+=dataList[i][1]
            toptenNumber=0
            if len(dataList)<=10:
                pie_data=[]
                labels=[]
                for i in range(len(dataList)):
                    pie_data.append(str(dataList[i][1]))
                    labels.append("%s=%s" % (dataList[i][0],str(dataList[i][1])))
                title = '%s PR\'s Attributes Statistics (Total %s PRs)' % (title_name,totalPR)
            else:
                for i in range(10):
                    toptenNumber+=dataList[i][1]
                otherNumber=totalNumber-toptenNumber
                pie_data=[]
                labels=[]
                for i in range(10):
                    pie_data.append(str(dataList[i][1]))
                    labels.append("%s=%s" % (dataList[i][0],str(dataList[i][1])))
                pie_data.append(str(otherNumber))
                labels.append('Other=%s' % str(otherNumber))
                title = '%s PR\'s Top Ten Attributes Statistics (Total %s PRs)' % (title_name,totalPR)
            name='attributes'
            legendPie2(pie_data,labels,title,title2,version,name)
            #print blockerList
            #print
            for i in range(len(blockerList)):
                if not blockerList[i]:
                    blockerList[i]="None"
            checked=[]
            totalNumber=len(blockerList)
            for item in blockerList:
                if item not in checked:
                    checked.append(item)
            blockerDirectory={}
            for item in checked:
                blockerDirectory[item]= '0'
            for item in blockerList:
                for key, value in blockerDirectory.items():
                    if re.match(r'^%s$' % key, item):
                        count=int(blockerDirectory[key])
                        count+=1
                        blockerDirectory[key]=count
            dataList=sorted(blockerDirectory.iteritems(), key=lambda d:d[1], reverse = True )
            pie_data=[]
            labels=[]
            for i in range(len(dataList)):
                pie_data.append(str(dataList[i][1]))
                labels.append("%s Blocker=%s" % (dataList[i][0],str(dataList[i][1])))
            title = '%s PR\'s Blocker Statistics (Total %s PRs)' % (title_name,totalPR)
            name='blocker'
            legendPie2(pie_data,labels,title,title2,version,name)
            checked=[]
            totalNumber=len(classList)
            for item in classList:
                if item not in checked:
                    checked.append(item)
            classDirectory={}
            for item in checked:
                classDirectory[item]= '0'
            for item in classList:
                for key, value in classDirectory.items():
                    if re.match(r'%s' % key, item):
                        count=int(classDirectory[key])
                        count+=1
                        classDirectory[key]=count
            dataList=sorted(classDirectory.iteritems(), key=lambda d:d[1], reverse = True )
            pie_data=[]
            labels=[]
            for i in range(len(dataList)):
                pie_data.append(str(dataList[i][1]))
                labels.append("%s=%s" % (dataList[i][0],str(dataList[i][1])))
            title = '%s PR\'s Class Statistics (Total %s PRs)' % (title_name,totalPR)
            name='class'
            legendPie2(pie_data,labels,title,title2,version,name)
            name='all'
            #write_HTML(all_prList,version,title2,name)
            write_HTML(data[1],version,title2,name)
            name='info_feedback'
            write_HTML(info_feedback_prList,version,title2,name)
            name='open'
            write_HTML(open_prList,version,title2,name)
            name='closed'
            write_HTML(closed_prList,version,title2,name)
            name='info'
            write_HTML(info_prList,version,title2,name)
            name='feedback'
            write_HTML(feedback_prList,version,title2,name)
            name='monitored'
            write_HTML(monitored_prList,version,title2,name)
            name='analyzed'
            write_HTML(analyzed_prList,version,title2,name)
            name='assigned'
            write_HTML(assigned_prList,version,title2,name)
            name='info_feedback_monitored'
            info_feedback_monitored_prList=info_prList+feedback_prList+monitored_prList
            write_HTML(info_feedback_monitored_prList,version,title2,name)
            name='blocker'
            write_HTML(blocker_prList,version,title2,name)
            name='unclosed_blocker'
            write_HTML(unclosed_blocker_prList,version,title2,name)
            name='open_lifetime'
            write_HTML(open_lifetime_prList,version,title2,name)
            name='info_lifetime'
            write_HTML(info_lifetime_prList,version,title2,name)
            name='feedback_lifetime'
            write_HTML(feedback_lifetime_prList,version,title2,name)
            name='info_feedback_lifetime'
            write_HTML(info_feedback_lifetime_prList,version,title2,name)
            write_search_pr_html(version,title2,all_prList,open_prList,info_feedback_prList,blocker_prList,unclosed_blocker_prList)
            start_end_date=get_start_end_date(data)
            if not set_start_date:
                start_date=start_end_date[0]
                end_date=start_end_date[1]
                end_date_list=get_date_list(start_date,end_date,int(duration))
                all_list=[]
                all_closed_list=[]
                all_blocker_list=[]
                all_open_list=[]
                total_list=[]
                blocker_list=[]
                open_list=[]
                closed_list=[]
                info_feedback_list=[]
                result=[]
                for i in range(len(end_date_list)):
                    result=query_PR_weekly(data,start_date,end_date_list[i])
                    all_list.append(result[0])
                    all_blocker_list.append(result[1])
                    all_open_list.append(result[3])
                    all_closed_list.append(result[4])
                    if i==0:
                        result=query_PR_weekly(data,start_date,end_date_list[i])
                        total_list.append(result[0])
                        blocker_list.append(result[1])
                        info_feedback_list.append(result[2])
                        open_list.append(result[3])
                        closed_list.append(result[4])
                    else:
                        result=query_PR_weekly(data,end_date_list[i-1],end_date_list[i])
                        total_list.append(result[0])
                        blocker_list.append(result[1])
                        info_feedback_list.append(result[2])
                        open_list.append(result[3])
                        closed_list.append(result[4])
                totalPR=all_list[-1]  
                index=0
                for i in range(len(all_list)):
                    if all_list[i]==all_list[-1]:
                        index=i 
                        break     
                for i in range(len(all_list)):
                    if i>index:
                        all_list[i]=1.7E+308
                        all_blocker_list[i]=1.7E+308
                        all_closed_list[i]=1.7E+308
                        all_open_list[i]=1.7E+308
                        total_list[i]=1.7E+308
                        blocker_list[i]=1.7E+308
                        info_feedback_list[i]=1.7E+308  
                        open_list[i]=1.7E+308
                        closed_list[i]=1.7E+308         
                title = '%s PR\'s Weekly Trending Statistics (Total %s PRs)' % (title_name,totalPR)
                name='weekly_trend'
                trendingLine(total_list,blocker_list,info_feedback_list,end_date_list,title,title2,version,name)
                title = '%s PR\'s Arrived Trending Statistics (Total %s PRs)' % (title_name,totalPR)
                name='weekly_arrived'
                multicylinder_weekly(all_list,total_list,closed_list,open_list,end_date_list,title,title2,version,name)
                title = '%s PR\'s Total Trending Statistics (Total %s PRs)' % (title_name,totalPR)
                name='total_trend'
                trendingLine_all(all_list,all_closed_list,all_blocker_list,end_date_list,title,title2,version,name)
                title = '%s PR\'s Closed Rate Trending Statistics (Total %s PRs)' % (title_name,totalPR)
                name='closed_rate'
                multicylinder(all_list,all_closed_list,all_open_list,end_date_list,title,title2,version,name) 
                if len(valid_userlist)>30:
                    user_width=1206
                else:
                    user_width=600
                if len(end_date_list)>11:
                    rate_width=1206
                else:
                    rate_width=600
                if len(end_date_list)>21:
                    trend_width=1206
                else:
                    trend_width=600
                
                #write_index(version,title2,all_prList,open_prList,info_feedback_prList,blocker_prList,unclosed_blocker_prList,rate_width,trend_width,category_width,user_width)
                write_index(expr,version,title2,all_prList,open_prList,info_feedback_prList,blocker_prList,unclosed_blocker_prList,open_lifetime_prList,info_lifetime_prList,feedback_lifetime_prList,info_feedback_lifetime_prList,rate_width,trend_width,category_width,user_width)
            else:
                start_date=adjust_start_date(set_start_date)
                end_date=start_end_date[1]
                end_date_list=get_date_list(start_date,end_date,int(duration))        
                all_list=[]
                all_closed_list=[]
                all_blocker_list=[]
                all_open_list=[]
                total_list=[]
                blocker_list=[]
                open_list=[]
                closed_list=[]
                info_feedback_list=[]
                result=[]
                for i in range(len(end_date_list)):
                    result=query_PR_weekly(data,start_date,end_date_list[i])
                    all_list.append(result[0])
                    all_blocker_list.append(result[1])
                    all_open_list.append(result[3])
                    all_closed_list.append(result[4])
                    if i==0:
                        result=query_PR_weekly(data,start_date,end_date_list[i])
                        total_list.append(result[0])
                        blocker_list.append(result[1])
                        info_feedback_list.append(result[2])
                        open_list.append(result[3])
                        closed_list.append(result[4])
                    else:
                        result=query_PR_weekly(data,end_date_list[i-1],end_date_list[i])
                        total_list.append(result[0])
                        blocker_list.append(result[1])
                        info_feedback_list.append(result[2])
                        open_list.append(result[3])
                        closed_list.append(result[4])
                totalPR=all_list[-1]  
                index=0
                for i in range(len(all_list)):
                    if all_list[i]==all_list[-1]:
                        index=i 
                        break     
                for i in range(len(all_list)):
                    if i>index:
                        all_list[i]=1.7E+308
                        all_blocker_list[i]=1.7E+308
                        all_closed_list[i]=1.7E+308
                        all_open_list[i]=1.7E+308
                        total_list[i]=1.7E+308
                        blocker_list[i]=1.7E+308
                        info_feedback_list[i]=1.7E+308  
                        open_list[i]=1.7E+308
                        closed_list[i]=1.7E+308         
                title = '%s PR\'s Weekly Trending Statistics (Total %s PRs)' % (title_name,totalPR)
                name='weekly_trend'
                trendingLine(total_list,blocker_list,info_feedback_list,end_date_list,title,title2,version,name)
                title = '%s PR\'s Arrived Trending Statistics (Total %s PRs)' % (title_name,totalPR)
                name='weekly_arrived'
                multicylinder_weekly(all_list,total_list,closed_list,open_list,end_date_list,title,title2,version,name)
                start_date=start_end_date[0]
                end_date=start_end_date[1]
                end_date_list=[]
                end_date_list=get_date_list(adjust_start_date(set_start_date),end_date,int(duration))
                all_list=[]
                all_closed_list=[]
                all_blocker_list=[]
                all_open_list=[]
                total_list=[]
                blocker_list=[]
                open_list=[]
                closed_list=[]
                info_feedback_list=[]
                result=[]
                for i in range(len(end_date_list)):
                    result=query_PR_weekly(data,start_date,end_date_list[i])
                    all_list.append(result[0])
                    all_blocker_list.append(result[1])
                    all_open_list.append(result[3])
                    all_closed_list.append(result[4])
                    if i==0:
                        result=query_PR_weekly(data,start_date,end_date_list[i])
                        total_list.append(result[0])
                        blocker_list.append(result[1])
                        info_feedback_list.append(result[2])
                        open_list.append(result[3])
                        closed_list.append(result[4])
                    else:
                        result=query_PR_weekly(data,end_date_list[i-1],end_date_list[i])
                        total_list.append(result[0])
                        blocker_list.append(result[1])
                        info_feedback_list.append(result[2])
                        open_list.append(result[3])
                        closed_list.append(result[4])
                totalPR=all_list[-1]  
                index=0
                for i in range(len(all_list)):
                    if all_list[i]==all_list[-1]:
                        index=i 
                        break     
                for i in range(len(all_list)):
                    if i>index:
                        all_list[i]=1.7E+308
                        all_blocker_list[i]=1.7E+308
                        all_closed_list[i]=1.7E+308
                        all_open_list[i]=1.7E+308
                        total_list[i]=1.7E+308
                        blocker_list[i]=1.7E+308
                        info_feedback_list[i]=1.7E+308  
                        open_list[i]=1.7E+308
                        closed_list[i]=1.7E+308         
                title = '%s PR\'s Total Trending Statistics (Total %s PRs)' % (title_name,totalPR)
                name='total_trend'
                trendingLine_all(all_list,all_closed_list,all_blocker_list,end_date_list,title,title2,version,name)
                title = '%s PR\'s Closed Rate Trending Statistics (Total %s PRs)' % (title_name,totalPR)
                name='closed_rate'
                multicylinder(all_list,all_closed_list,all_open_list,end_date_list,title,title2,version,name)
                if len(valid_userlist)>30:
                    user_width=1206
                else:
                    user_width=600
                if len(end_date_list)>11:
                    rate_width=1206
                else:
                    rate_width=600
                if len(end_date_list)>21:
                    trend_width=1206
                else:
                    trend_width=600
                
                write_index(expr,version,title2,all_prList,open_prList,info_feedback_prList,blocker_prList,unclosed_blocker_prList,open_lifetime_prList,info_lifetime_prList,feedback_lifetime_prList,info_feedback_lifetime_prList,rate_width,trend_width,category_width,user_width)
                
            
            
           
