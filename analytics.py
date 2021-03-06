import csv 
import numpy as np
import math 
from datetime import datetime 
from matplotlib.figure import Figure

MONTHS_OF_YEAR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Nov", "Dec"]

class DayAnalytics:
    """ holds statistics for one day """ 
    def __init__(self, date):
        self.date = date 
        self.confessions = []
        self.word_freq_map = {} 

    def updateAnalytics(self): 
        new_freq_map = {} 
        for confession in self.confessions:
            for word in confession.split(" "):
                lower_cased = word.lower(); 
                if lower_cased in new_freq_map:
                    new_freq_map[lower_cased] += 1
                else: 
                    new_freq_map[lower_cased] = 1
        self.word_freq_map = new_freq_map
    
    def getWordFreqs(self, words, use_avg=False):
        total = 0 
        for word in words: 
            if word in self.word_freq_map:
                total += self.word_freq_map[word]
        return float(total) / float(len(self.confessions)) if use_avg else float(total)

    def getPostedConfessiosn(self):
        return len(self.confessions)

class Analytics: 
    def __init__(self, datasource, timestamp_format_str='%m/%d/%Y %H:%M:%S'):
        self.datasource = datasource 
        self.toDatetime = (lambda timestamp_str: datetime.strptime(timestamp_str, timestamp_format_str))
        self.days_aggregate = self.load(datasource)

    def load(self, file_path): 
        days = []
        with open(file_path, newline='', encoding="utf-8-sig") as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            current_day = None
            for row in reader:
                row_date = self.toDatetime(row[0])
                if current_day == None:
                    current_day = DayAnalytics(row_date)
                elif current_day.date != row_date:
                    #finalize analytics of last day and add to days
                    current_day.updateAnalytics()
                    days.append(current_day)

                    #then switch to new day 
                    current_day = DayAnalytics(row_date)
                
                current_day.confessions.append(row[1])
            days.append(current_day)
        return days

    def createBaseDailyFigure(self, custom_range=None):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.set_xlabel('Date posted')
        xticks = []
        for i in range(len(self.days_aggregate)): 
            if self.days_aggregate[i].date.day == 1:
                #put xtick on first day of month 
                #todo; this assume ocnfessions posted every day 
                xticks.append({'index':i, 'label': self.days_aggregate[i].date.month})
        axis.set_xticks([x['index'] for x in xticks])
        axis.set_xticklabels([MONTHS_OF_YEAR[x['label']] for x in xticks])

        return fig

    def createDailyFigure(self, ys, y_label, NUM_Y_TICKS=9.0):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        xs = range(len(self.days_aggregate))
        ys = ys
        axis.bar(xs, ys)
        axis.set_ylabel(y_label)
        axis.set_xlabel('Date posted')
        xticks = []
        for i in range(len(self.days_aggregate)): 
            if self.days_aggregate[i].date.day == 1:
                #put xtick on first day of month 
                #todo; this assume ocnfessions posted every day 
                xticks.append({'index':i, 'label': self.days_aggregate[i].date.month})
        axis.set_xticks([x['index'] for x in xticks])
        axis.set_xticklabels([MONTHS_OF_YEAR[x['label']] for x in xticks])

        y_tick_interval = (max(ys)+1.0) / NUM_Y_TICKS + 0.1; 
        axis.set_yticks(np.arange(0, max(ys)+1, math.ceil(y_tick_interval)))
        return fig

    def addWordFrequency(self, fig, words, color='blue', use_avg=False): 
        axis = fig.add_subplot(1, 1, 1)
        xs = range(len(self.days_aggregate))
        word_freq_data = [day.getWordFreqs(words, use_avg=use_avg) for day in self.days_aggregate]
        axis.bar(xs, word_freq_data, color=color)
        return fig 

    def addNumLine(self, fig):
        axis = fig.add_subplot(1, 1, 1)
        axis2 = axis.twinx()
        xs = range(len(self.days_aggregate))
        day_count_data = [len(day.confessions) for day in self.days_aggregate]
        axis2.plot(xs, day_count_data, color='black')
        return fig 