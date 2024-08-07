#
# aggregate per-month statistics for people
#
import sys, datetime
import csv

class CSVStat:
    def __init__ (self, name, email, employer, date):
        self.name = name
        self.email = email
        self.employer = employer
        self.added = self.removed = self.changesets = 0
        self.date = date
    def accumulate (self, p):
        self.added = self.added + p.added
        self.removed = self.removed + p.removed
        self.changesets += 1

PeriodCommitHash = { }

def AccumulatePatch (p, Aggregate):
    if (Aggregate == 'week'):
        date = "%.2d-%.2d"%(p.date.isocalendar()[0], p.date.isocalendar()[1])
    elif (Aggregate == 'year'):
        date = "%.2d"%(p.date.year)
    else:
        date = "%.2d-%.2d-01"%(p.date.year, p.date.month)
    authdatekey = "%s-%s"%(p.author.name, date)
    if authdatekey not in PeriodCommitHash:
        empl = p.author.emailemployer (p.email, p.date)
        stat = CSVStat (p.author.name, p.email, empl, date)
        PeriodCommitHash[authdatekey] = stat
    else:
        stat = PeriodCommitHash[authdatekey]
    stat.accumulate (p)

ChangeSets = []
FileTypes = []

def store_patch(patch):
    if not patch.merge:
        employer = patch.author.emailemployer(patch.email, patch.date)
        employer = employer.name.replace('"', '.').replace ('\\', '.')
        author = patch.author.name.replace ('"', '.').replace ('\\', '.')
        author = patch.author.name.replace ("'", '.')
        try:
            domain = patch.email.split('@')[1]
        except:
            domain = patch.email
        ChangeSets.append([patch.commit, str(patch.date),
                           patch.email, domain, author, employer,
                           patch.added, patch.removed])
        for (filetype, (added, removed)) in patch.filetypes.items():
            FileTypes.append([patch.commit, filetype, added, removed])


def save_csv (prefix='data'):
    # Dump the ChangeSets
    if len(ChangeSets) > 0:
        fd = open('%s-changesets.csv' % prefix, 'w')
        writer = csv.writer (fd, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow (['Commit', 'Date', 'Domain',
                          'Email', 'Name', 'Affliation',
                          'Added', 'Removed'])
        for commit in ChangeSets:
            writer.writerow(commit)

    # Dump the file types
    if len(FileTypes) > 0:
        fd = open('%s-filetypes.csv' % prefix, 'w')
        writer = csv.writer (fd, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow (['Commit', 'Type', 'Added', 'Removed'])
        for commit in FileTypes:
            writer.writerow(commit)



def OutputCSV (file):
    if file is None:
        return
    writer = csv.writer (file, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow (['Name', 'Email', 'Affliation', 'Date',
                      'Added', 'Removed', 'Changesets'])
    for date, stat in PeriodCommitHash.items():
        # sanitise names " is common and \" sometimes too
        empl_name = stat.employer.name.replace ('"', '.').replace ('\\', '.')
        author_name = stat.name.replace ('"', '.').replace ('\\', '.')
        writer.writerow ([author_name, stat.email, empl_name, stat.date,
                          stat.added, stat.removed, stat.changesets])

def OutputHackersCSV (file, hlist):
    if file is None:
        return
    file.write ("Name,Last affiliation,Activity Start,Activity End,Commits,Lines Added,Lines Removed\n")
    for hacker in hlist:
        if len(hacker.patches) > 0:
            file.write ("\"%s\",%s,%s,%s,%d,%d,%d\n" %
                        (hacker.name,
                         hacker.emailemployer (None, hacker.activity_end).name,
                         hacker.activity_start, hacker.activity_end,
                         len(hacker.patches),
                         hacker.added, hacker.removed))


def OutputEmployersCSV (file, elist):
    if file is None:
        return
    file.write ("Name,Category,Hackers,Commits,Lines Added,Lines Removed\n")
    for employer in elist:
        if employer.count > 0:
            file.write ("\"%s\",\"%s\",%d,%d,%d,%d\n" %
                        (employer.name,
                         employer.category,
                         len(employer.hackers),
                         employer.count,
                         employer.added,
                         employer.removed))

def OutputCategoriesCSV (file, elist):
    if file is None:
        return
    file.write ("Category,Organisations,Hackers,Commits,Lines Added,Lines Removed\n")
    categories = { }
    for employer in elist:
        if employer.count > 0:
            if employer.category not in categories:
                categories[employer.category] = dict(organisations = 0, hackers = 0, count = 0, added = 0, removed = 0)
            categories[employer.category]['hackers'] = categories[employer.category]['hackers'] + len(employer.hackers)
            categories[employer.category]['organisations'] = categories[employer.category]['organisations'] + 1
            categories[employer.category]['count'] = categories[employer.category]['count'] + employer.count
            categories[employer.category]['added'] = categories[employer.category]['added'] + employer.added
            categories[employer.category]['removed'] = categories[employer.category]['removed'] + employer.removed
    for category in categories:
        file.write ("\"%s\",%d,%d,%d,%d,%d\n" %
                    (category,
                     categories[category]['organisations'],
                     categories[category]['hackers'],
                     categories[category]['count'],
                     categories[category]['added'],
                     categories[category]['removed']))


__all__ = [  'AccumulatePatch', 'OutputCSV', 'OutputHackersCSV', 'OutputEmployersCSV', 'OutputCategoriesCSV', 'store_patch' ]



