#
# A new home for the reporting code.
#
# This code is part of the LWN git data miner.
#
# Copyright 2007-16 Eklektix, Inc.
# Copyright 2007-16 Jonathan Corbet <corbet@lwn.net>
#
# This file may be distributed under the terms of the GNU General
# Public License, version 2.
#

import sys

Outfile = sys.stdout
HTMLfile = None
rSTfile = None
ListCount = 999999


def SetOutput(file):
    global Outfile
    Outfile = file

def SetHTMLOutput(file):
    global HTMLfile
    HTMLfile = file

def SetrSTOutput(file):
    global rSTfile
    rSTfile = file

def SetMaxList(max):
    global ListCount
    ListCount = max


def Write(stuff):
    Outfile.write(stuff)



THead = '''<p>
<table cellspacing=3 class="OddEven">
<tr><th colspan=3>%s</th></tr>
'''

RHead = '''
.. table:: %s
   :widths: auto

   ====================================  =====
   Name                                  Count
   ====================================  =====
'''

def BeginReport(title):
    Outfile.write('\n%s\n' % title)
    if HTMLfile:
        HTMLfile.write(THead % title)
    if rSTfile:
        rSTfile.write(RHead % title)

TRow = ' <tr><td>%s</td><td align="right">%d</td><td align="right">%.1f%%</td></tr>\n'
TRowStr = ' <tr><td>%s</td><td align="right">%d</td><td>%s</td></tr>\n'

def ReportLine(text, count, pct):
    if count == 0:
        return
    Outfile.write ('%-25s %4d (%.1f%%)\n' % (text, count, pct))
    if HTMLfile:
        HTMLfile.write(TRow % (text, count, pct))
    if rSTfile:
        rSTfile.write("   %-36s  %d (%.1f%%)\n" % (text.strip(), count, pct))

def ReportLineStr(text, count, extra):
    if count == 0:
        return
    Outfile.write ('%-25s %4d %s\n' % (text, count, extra))
    if HTMLfile:
        HTMLfile.write(TRowStr % (text, count, extra))
    if rSTfile:
        rSTfile.write('%-36s %d %s\n' % (text, count, extra))

def EndReport():
    if HTMLfile:
        HTMLfile.write('</table>\n\n')
    if rSTfile:
        rSTfile.write('   ====================================  =====\n\n')
        
#
# Comparison and report generation functions.
#
def ComparePCount(h):
    return len(h.patches)

def ReportByPCount(hlist, cscount):
    hlist.sort(key = ComparePCount, reverse = True)
    count = 0
    BeginReport('Developers with the most changesets')
    for h in hlist:
        pcount = len(h.patches)
        changed = max(h.added, h.removed)
        delta = h.added - h.removed
        if pcount > 0:
            ReportLine(h.name, pcount, (pcount*100.0)/cscount)
        count += 1
        if count >= ListCount:
            break
    EndReport()
            
def CompareLChanged(h):
    return h.changed

def ReportByLChanged(hlist, totalchanged):
    hlist.sort(key = CompareLChanged, reverse = True)
    count = 0
    BeginReport('Developers with the most changed lines')
    for h in hlist:
        pcount = len(h.patches)
        if h.changed > 0:
            ReportLine(h.name, h.changed, (h.changed*100.0)/totalchanged)
        count += 1
        if count >= ListCount:
            break
    EndReport()
            
def CompareLRemoved(h):
    return (h.removed - h.added)

def ReportByLRemoved(hlist, totalremoved):
    hlist.sort(key = CompareLRemoved, reverse = True)
    count = 0
    BeginReport('Developers with the most lines removed')
    for h in hlist:
        pcount = len(h.patches)
        changed = max(h.added, h.removed)
        delta = h.added - h.removed
        if delta < 0:
            ReportLine(h.name, -delta, (-delta*100.0)/totalremoved)
        count += 1
        if count >= ListCount:
            break
    EndReport()

def CompareEPCount(e):
    return e.count

def ReportByPCEmpl(elist, cscount):
    elist.sort(key = CompareEPCount, reverse = True)
    count = 0
    BeginReport('Top changeset contributors by employer')
    for e in elist:
        if e.count != 0:
            ReportLine(e.name, e.count, (e.count*100.0)/cscount)
        count += 1
        if count >= ListCount:
            break
    EndReport()


def CompareELChanged(e):
    return e.changed

def ReportByELChanged(elist, totalchanged):
    elist.sort(key = CompareELChanged, reverse = True)
    count = 0
    BeginReport('Top lines changed by employer')
    for e in elist:
        if e.changed != 0:
            ReportLine(e.name, e.changed, (e.changed*100.0)/totalchanged)
        count += 1
        if count >= ListCount:
            break
    EndReport()



def CompareSOBs(h):
    return len(h.signoffs)

def ReportBySOBs(hlist):
    hlist.sort(key = CompareSOBs, reverse = True)
    totalsobs = 0
    for h in hlist:
        totalsobs += len(h.signoffs)
    count = 0
    BeginReport('Developers with the most signoffs (total %d)' % totalsobs)
    for h in hlist:
        scount = len(h.signoffs)
        if scount > 0:
            ReportLine(h.name, scount, (scount*100.0)/totalsobs)
        count += 1
        if count >= ListCount:
            break
    EndReport()

#
# Reviewer reporting.
#
def CompareRevs(h):
    return len(h.reviews)

def ReportByRevs(hlist):
    hlist.sort(key = CompareRevs, reverse = True)
    totalrevs = 0
    for h in hlist:
        totalrevs += len(h.reviews)
    count = 0
    BeginReport('Developers with the most reviews (total %d)' % totalrevs)
    for h in hlist:
        scount = len(h.reviews)
        if scount > 0:
            ReportLine(h.name, scount, (scount*100.0)/totalrevs)
        count += 1
        if count >= ListCount:
            break
    EndReport()

#
# tester reporting.
#
def CompareTests(h):
    return len(h.tested)

def ReportByTests(hlist):
    hlist.sort(key = CompareTests, reverse = True)
    totaltests = 0
    for h in hlist:
        totaltests += len(h.tested)
    count = 0
    BeginReport('Developers with the most test credits (total %d)' % totaltests)
    for h in hlist:
        scount = len(h.tested)
        if scount > 0:
            ReportLine(h.name, scount, (scount*100.0)/totaltests)
        count += 1
        if count >= ListCount:
            break
    EndReport()

def CompareTestCred(h):
    return h.testcred

def ReportByTestCreds(hlist):
    hlist.sort(key = CompareTestCred, reverse = True)
    totaltests = 0
    for h in hlist:
        totaltests += h.testcred
    count = 0
    BeginReport('Developers who gave the most tested-by credits (total %d)' % totaltests)
    for h in hlist:
        if h.testcred > 0:
            ReportLine(h.name, h.testcred, (h.testcred*100.0)/totaltests)
        count += 1
        if count >= ListCount:
            break
    EndReport()



#
# Reporter reporting.
#
def CompareReports(h):
    return len(h.reports)

def ReportByReports(hlist):
    hlist.sort(key = CompareReports, reverse = True)
    totalreps = 0
    for h in hlist:
        totalreps += len(h.reports)
    count = 0
    BeginReport('Developers with the most report credits (total %d)' % totalreps)
    for h in hlist:
        scount = len(h.reports)
        if scount > 0:
            ReportLine(h.name, scount, (scount*100.0)/totalreps)
        count += 1
        if count >= ListCount:
            break
    EndReport()

def CompareRepCred(h):
    return h.repcred

def ReportByRepCreds(hlist):
    hlist.sort(key = CompareRepCred, reverse = True)
    totalreps = 0
    for h in hlist:
        totalreps += h.repcred
    count = 0
    BeginReport('Developers who gave the most report credits (total %d)' % totalreps)
    for h in hlist:
        if h.repcred > 0:
            ReportLine(h.name, h.repcred, (h.repcred*100.0)/totalreps)
        count += 1
        if count >= ListCount:
            break
    EndReport()

#
# Versions.
#
def CompareVersionCounts(h):
    if h.versions:
        return len(h.versions)
    return -1

def MissedVersions(hv, allv):
    missed = [v for v in allv if v not in hv]
    missed.reverse()
    return ' '.join(missed)

def ReportVersions(hlist):
    hlist.sort(key = CompareVersionCounts, reverse = True)
    BeginReport('Developers represented in the most kernel versions')
    count = 0
    allversions = hlist[0].versions
    for h in hlist:
        ReportLineStr(h.name, len(h.versions), MissedVersions(h.versions, allversions))
        count += 1
        if count >= ListCount:
            break
    EndReport()


def CompareESOBs(e):
    return e.sobs

def ReportByESOBs(elist):
    elist.sort(key = CompareESOBs, reverse = True)
    totalsobs = 0
    for e in elist:
        totalsobs += e.sobs
    count = 0
    BeginReport('Employers with the most signoffs (total %d)' % totalsobs)
    for e in elist:
        if e.sobs > 0:
            ReportLine(e.name, e.sobs, (e.sobs*100.0)/totalsobs)
        count += 1
        if count >= ListCount:
            break
    EndReport()
   
def CompareHackers(e):
    return len(e.hackers)

def ReportByEHackers(elist):
    elist.sort(key = CompareHackers, reverse = True)
    totalhackers = 0
    for e in elist:
        totalhackers += len(e.hackers)
    count = 0
    BeginReport('Employers with the most hackers (total %d)' % totalhackers)
    for e in elist:
        nhackers = len(e.hackers)
        if nhackers > 0:
            ReportLine(e.name, nhackers, (nhackers*100.0)/totalhackers)
        count += 1
        if count >= ListCount:
            break
    EndReport()


def DevReports(hlist, totalchanged, cscount, totalremoved):
    ReportByPCount(hlist, cscount)
    ReportByLChanged(hlist, totalchanged)
    ReportByLRemoved(hlist, totalremoved)
    ReportBySOBs(hlist)
    ReportByRevs(hlist)
    ReportByTests(hlist)
    ReportByTestCreds(hlist)
    ReportByReports(hlist)
    ReportByRepCreds(hlist)

def EmplReports(elist, totalchanged, cscount):
    ReportByPCEmpl(elist, cscount)
    ReportByELChanged(elist, totalchanged)
    ReportByESOBs(elist)
    ReportByEHackers(elist)

#
# Who are the unknown hackers?
#
def IsUnknown(h):
    empl = h.employer[0][0][1].name
    return h.email[0] == empl or empl == '(Unknown)'

def ReportUnknowns(hlist, cscount):
    #
    # Trim the list to just the unknowns; try to work properly whether
    # mapping to (Unknown) is happening or not.
    #
    ulist = [ h for h in hlist if IsUnknown(h) ]
    ulist.sort(key = ComparePCount, reverse = True)
    count = 0
    BeginReport('Developers with unknown affiliation')
    for h in ulist:
        pcount = len(h.patches)
        if pcount > 0:
            ReportLine(h.name, pcount, (pcount*100.0)/cscount)
            count += 1
        if count >= ListCount:
            break
    EndReport()



def ReportByFileType(hacker_list):
    total = {}
    total_by_hacker = {}

    BeginReport('Developer contributions by type')
    for h in hacker_list:
        by_hacker = {}
        for patch in h.patches:
            # Get a summary by hacker
            for (filetype, (added, removed)) in patch.filetypes.iteritems():
                if by_hacker.has_key(filetype):
                    by_hacker[filetype][patch.ADDED] += added
                    by_hacker[filetype][patch.REMOVED] += removed
                else:
                    by_hacker[filetype] = [added, removed]

                # Update the totals
                if total.has_key(filetype):
                    total[filetype][patch.ADDED] += added
                    total[filetype][patch.REMOVED] += removed
                else:
                    total[filetype] = [added, removed, []]

        # Print a summary by hacker
        # FIXME why isn't this using Outfile?
        print(h.name)
        for filetype, counters in by_hacker.iteritems():
            print('\t', filetype, counters)
            h_added = by_hacker[filetype][patch.ADDED]
            h_removed = by_hacker[filetype][patch.REMOVED]
            total[filetype][2].append([h.name, h_added, h_removed])

    # Print the global summary
    BeginReport('Contributions by type and developers')
    for filetype, (added, removed, hackers) in total.iteritems():
        print(filetype, added, removed)
        for h, h_added, h_removed in hackers:
            print('\t%s: [%d, %d]' % (h, h_added, h_removed))

    # Print the very global summary
    BeginReport('General contributions by type')
    for filetype, (added, removed, hackers) in total.iteritems():
        print(filetype, added, removed)

#
# The file access report is a special beast.
#
def FileAccessReport(name, accesses, total):
    outf = open(name, 'w')
    files = sorted(accesses)
    for file in files:
        a = accesses[file]
        outf.write('%6d %6.1f%% %s\n' % (a, (100.0*a)/total, file))
    outf.close()
