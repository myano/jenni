#!/usr/bin/env python
"""
learn.py - jenni Learn module
Copyright 2010-2013, Micheal Yanovich (yanovich.net)
 
Learn module created by:
Real name: (author wishes to remain anonymous)
Pseudonyms: Zapp (IRC), gmaster350 (@gmail.com, github)
 
more info:
* jenni: https://github.com/myano/jenni/
* Phenny: http://inamidst.com/phenny/
 
 
About: The purpose of the Learn module is to create a
chat bot which learns how to give appropriate responses.
Based upon feedback given to it, jenni will learn to associate
words and combinations of words with specific replies.
"""
import random
import sys
 
with open('dictionary.txt', 'r') as inf: ### read in dictionary from file ###
    word = eval(inf.read())
with open('list_of_replies.txt', 'r') as data: ### read in replies from file ###
    replies = eval(data.read())
 
prevMessage = str() ### previous message stored here ###
prevReply = int() ### previous reply index stored here ###
nick = str()
 
def isAddressed(messageIn): ### Boolean; checks if input begins with "[nick]:" ###
    global nick
    if messageIn[0:len(nick)+1] == str(nick + ':'):
        return True
    else:
        return False
 
def isNumber(messageIn): ### Boolean; checks if str input contains only numeral chars ###
    result = True
    for i in range(0, len(messageIn)): ### Go through all characters, in case the number has more than one digit ###
        if not ((messageIn[i] == '0') or (messageIn[i] == '1') or (messageIn[i] == '2') or (messageIn[i] == '3') or (messageIn[i] == '4') or (messageIn[i] == '5') or (messageIn[i] == '6') or (messageIn[i] == '7') or (messageIn[i] == '8') or (messageIn[i] == '9')):
            result = False ### If any chars in messageIn are not a number, set to false ###
    if result == True:
        return True
    else:
        return False
 
def isScore(messageIn): ### Boolean; Checks if message has the format of a score ###
    lenMessage = int(len(messageIn))
    scoreFlag = bool()
    if lenMessage < 4:
        scoreFlag = False
    if ((lenMessage == 4) and (messageIn[1] == '/')) or ((lenMessage == 5) and (messageIn[2] == '/') and (messageIn[0] != '-')): ### checks for the slash in appropriate place, also makes sure value is not negative ###
        scoreFlag = True
    else:
        scoreFlag = False
    return scoreFlag
 
def getScore(messageIn): ### Integer; Return score given by user in the score format ###
    if len(messageIn) == 5: ### If message has 5 chars, return value 10. This means values like 11, 15 will be treated as 10 ###
        num = int(10)
    elif len(messageIn) == 4: ### return first character if length is 4 ###
        num = int(messageIn[0])
    return num
 
def weightedSelection(messageIn):
    messageWords = list(messageIn.split()) ### turn string into list of words ###
    replyWeights = [] ### prepare list replyWeights ###
    for a in range(0, len(replies)):
            replyWeights.append(0) ### add as many values to replyWeights as there are replies, initializing all to 0 ###
   
    for b in range(0, len(replyWeights)):
        for c in range(0, len(messageWords)):
            messageWord = messageWords[c]
            replyWeights[b] += word[messageWord][b] ### for every word(c) in message, add weight of their reply(b) to replyWeights(b) ###
   
    randomRange = [] ### prepare list for numbers to be used for ranges ###
    for e in range(0, len(replyWeights)):
        rangeLimit = int(0) ### prepare number to add to ###
        for f in range(0, e):
            rangeLimit += int(replyWeights[f]) ### For all replies weights, set corresponding range upper limit as sum of all before it. i.e: that [2,3,5] becomes [2,5,10] ###
        randomRange.append(rangeLimit) ### append sum to randomRange ###
   
    rand = random.randint(0,randomRange[len(randomRange)-1])  ### generate random number up to the final value in randomRange ###
    numToReturn = 0 ### initialize number to return ###
    for n in range(len(randomRange)):
        if rand == randomRange[len(randomRange)-1]:
            numToReturn = len(randomRange)-1
        else:
            if rand > randomRange[n]:
                numToReturn = n-1
                break
    return int(numToReturn)
   
def getReplyAverage(num):
    replyWeightSum = 0 ### prepare arithmetic process ###
    wordList = list(word.keys()) ### create indexable copy of the dictionary ###
    lenWordList = len(wordList)
    for n in range(0, lenWordList):
        replyWeightSum += word[wordList[n]][num] ### for every word(n) in the dictionary, add the reply(num) to the sum. ((e.g: word[0], reply0 word[1], reply0 ..)). ###
    replyWeightAverage = int(replyWeightSum/len(wordList))
    return replyWeightAverage
 
def processMessage(messageIn):
    global prevMessage
    global prevReply
    messageOut = '' ### prepare message ###
    if isScore(messageIn):
        if isScore(prevMessage):
            messageOut += "You already gave me a score"
        else:
            score = int(getScore(messageIn)) ### Find out score from message, but only if text is a score. ###
            score -= 5
            if score > 0: ### Different messages for incrementing or decrementing scores ###
                messageOut += "Thanks!" ### Reply for high scores (6/10 to 10/10) ###
            elif score < 0:
                messageOut += "I'll try to improve." ### Reply for low scores (0/10 to 4/10) ###
            else:
                messageOut += "Thanks for helping!" ### Reply for score of 5/10 ###
           
            prevMessageWords = list(prevMessage.split())
            for i in range(0, len(prevMessageWords)):
                prevMessageWord = str(prevMessageWords[i])
                if score < 0:
                    if word[prevMessageWord][prevReply] < abs(int(score)): ### If decrement will result in negative value, set weight to zero ###
                        word[prevMessageWord][prevReply] = 0
                    else:
                        word[prevMessageWord][prevReply] += score
                else:
                    word[prevMessageWord][prevReply] += score
               
    else:
        messageWords = messageIn.split()
        for i in range(0, len(messageWords)):
            newestWord = str(messageWords[i])
            if newestWord not in word: ### if there are words in message which are not in the dictionary, add them, and initialize their values to average ###
                word[newestWord] = []
                for t in range(0, len(replies)):
                    word[newestWord].append(0)
                for v in range(0, len(replies)):
                    word[newestWord][v] += getReplyAverage(v)
        replyIndex = weightedSelection(messageIn) ### choose reply from weighted random ###
        messageOut = replies[replyIndex]
        prevReply = int(replyIndex)
    return messageOut
 
def learn (phenny, input):
    channelMessage = input ### Did this so I didn't have to change all the code to the new word ###
    reply = str("") ### prepare the reply ###
    global prevMessage ### call global values, so that they can be updated
    global nick
    nick = phenny.nick ### Set nick ###
    if not isAddressed(channelMessage): ### If bot is not directly addressed, instead check if the message is a command ###
        if channelMessage[0] == '.':       
            if channelMessage[0:8] == '.addWord':
                newWord = str(channelMessage[9:len(channelMessage)])
                if newWord in word:
                    reply += str('"' + newWord + '" exists in dictionary.')
                else:
                    word[newWord] = []
                    for x in range(0,len(replies)):
                        word[newWord].append(0)
                        word[newWord][x] += int(getReplyAverage(x)) ### set each reply weight for the new word to the mean-average weight of that reply across all words in the dictionary ###
                    reply += str('Added!')
           
            elif channelMessage[0:9] == '.addReply':
                newReply = channelMessage[10:len(channelMessage)]
                replies.append(str(newReply))
                for (key, value) in word.items():
                    value.append(0) ### go through all dictionary entries, and add a new value to each associated list of replies ###
                reply += str('Added!')
               
            elif channelMessage[0:11] == '.dictionary':
                reply += str(list(word.keys())) ### display the whole dictionary ###
           
            elif channelMessage[0:8] == '.replies':
                for i in range(0, len(replies)): ### display all replies, along with their reply index ####
                    reply += str("reply" + str(i) + ": '" + replies[i] + "', ")
           
            elif channelMessage[0:12] == '.wordWeights':
                wordPicked = channelMessage[13:len(channelMessage)]
                if wordPicked in word: ### Check if word exists in dictionary ###
                    for i in range(0, len(replies)): ### Display all reply weights, along with the reply index of each reply ###
                        reply += str("reply" + str(i) + ": " + str(word[wordPicked][i]) + "  ")
                else:
                    reply += str("Word not in dictionary")
           
            elif channelMessage[0:21] == '.setWeightsIndividual': ### manually set the weights of several words ###
                wordsPicked = channelMessage[22:len(channelMessage)].split()
                invalidCount = int(0)
                numberCount = int(0)
                for i in range(0, len(wordsPicked)):
                    if isNumber(wordsPicked[i]):
                        numberCount += 1
                    if (not isNumber(wordsPicked[i])) and (wordsPicked[i] not in word):
                        invalidCount += 1 ### If word is not in dictionary, increment invalidCount ###
                wordCount = int(len(wordsPicked) - numberCount)
                if not (numberCount == int(wordCount * len(replies))): ### check if there are enough weights for each word given ###
                    reply += str('Mismatch between at least one of the words and the number of replies')
                elif int(invalidCount) == wordCount:
                    reply += str('None of those words are in the dictionary') ### reply if no words given exist in the dictionary ###
                else:
                    wordsToSet = list()
                    weightList = list()
                    weightsToSet = dict() ### create a temporary second dictioary ###
                    for u in range(0, len(wordsPicked)):
                        if not isNumber(wordsPicked[u]):
                            wordsToSet.append(wordsPicked[u])
                        else:
                            weightList.append(int(wordsPicked[u]))
                    for v in range(0, wordCount):
                        weightsToSet[wordsToSet[v]] = []
                        for w in range(0, len(replies)):
                            weightsToSet[wordsToSet[v]].append(weightList[w])
                    for x in range(0, len(wordsToSet)):
                        for y in range(0, len(replies)):
                            word[wordsToSet[x]][y] = int(weightsToSet[wordsToSet[x]][y]) ### transfer the word weights from temporary dictionary to the main dictionary ###
                    reply += str('Weights changed!')
                   
            elif channelMessage[0:14] == '.setWeightsAll': ### Set the weights for several words at the same time, useful for associating whole sentences with a reply ###
                wordsPicked = channelMessage[15:len(channelMessage)].split()
                invalidCount = int(0) ### initialize number of words not in the dictionary ###
                numberCount = int(0) ### initialize quantity of numbers ###
                for j in range(0,len(wordsPicked)):
                    if isNumber(wordsPicked[j]):
                        numberCount += 1
                    if (not isNumber(wordsPicked[j])) and (wordsPicked[j] not in word):
                        invalidCount += 1
                wordCount = int(len(wordsPicked) - numberCount)
                if not (numberCount == len(replies)):
                    reply += str("The quantity of weights don't match the replies")
                elif int(invalidCount) == wordCount:
                    reply += str('None of those words are in the dictionary')
                else:  
                    wordsToSet = []
                    weightsToSet = []
                    for i in range(0, len(wordsPicked)):
                        if isNumber(wordsPicked[i]):
                            weightsToSet.append(int(wordsPicked[i]))
                        else:
                            if wordsPicked[i] in word:
                                wordsToSet.append(str(wordsPicked[i]))
                    for g in range(0, len(wordsToSet)):
                        for h in range(0, len(weightsToSet)):
                            word[wordsToSet[g]][h] = int(weightsToSet[h])
                    reply += str('Weights changed!')
           
            elif channelMessage[0:6] == ".debug":
                if showDebug == True:
                    showDebug = False
                    reply += str('debugging enabled.')
                else:
                    showDebug = True
                    reply += str('debugging disabled')
           
            elif channelMessage[0:12] == ".removeReply":
                replyPicked = channelMessage[13:len(channelMessage)]
                if replyPicked == 'last': ### removes the last entry in replies w###
                    replies.pop()
                    wordKeys = list(word.keys())
                    for key in range(len(word)): ### go through the dictionary, and remove each word's associated reply weight at the last index ###
                        word[wordKeys[key]].pop()
                    reply += str("Removed!") ### confirmation reply ###
                elif replyPicked[0:6] == "index ":
                    indexPicked = replyPicked[6:len(replyPicked)]
                    if isNumber(indexPicked):
                        if indexPicked < len(replies):
                            replies.pop(indexPicked)
                            reply += str("Removed!") ### confirmation reply ###
                        else:
                            reply += str("Out of range!") ### reply if the index chosen is greater than the length of the replies list ###
                    else:
                        reply += str("Only positive numbers, please!") ### reply if the index chosen contains a non-numeral character ###
                else:
                    reply += str("I didn't understand that. Usage: 'last' or 'index (int)'")
 
            elif channelMessage[0:12] == '.lastMessage':
                reply += str("'" + prevMessage + "'")
           
            elif channelMessage[0:10] == '.lastReply':
                reply += str('(reply' + str(prevReply) + ')' + replies[prevReply])
           
           
            elif channelMessage[0:10] == '.helpLearn':
               
                if channelMessage [0:20] == '.helpLearn help':
                    reply+= str("Usage: '.helpLearn (word)' --- Displays usage and description of a given command. You must omit the usual '.' at the start of the command. e.g: '.help addWord'")
           
                elif channelMessage[0:18] == '.helpLearn addWord':
                    reply += str("Usage: '.addWord (word)' --- manually adds a word to the dictionary, initializing all weight values to averages.")
               
                elif channelMessage[0:19] == '.helpLearn addReply':
                    reply += str("Usage: '.addReply (multiple words)' --- adds a new reply to the list of replies.")
           
                elif channelMessage[0:22] == '.helpLearn removeReply':
                    reply += str("Usage: '.removeReply [last | index (int)]' --- deletes a reply from the list of replies. '.removeReply last' removes last added reply, '.removeReply index n' removes reply at index n.")
           
                elif channelMessage[0:21] == '.helpLearn dictionary':
                    reply += str("Usage: '.dictionary' --- Displays all words in the dictionary.")
           
                elif channelMessage[0:18] == '.helpLearn replies':
                    reply += str("Usage: '.replies' --- Displays all replies in the list of replies, along with their index.")
           
                elif channelMessage[0:22] == '.helpLearn wordWeights':
                    reply += str("Usage: '.wordWeights (word)' --- Displays reply weights for specified word.")
               
                elif channelMessage[0:31] == '.helpLearn setWeightsIndividual':
                    reply += str("Usage: '.setWeightsIndividual (word) (int) (int...) (word) (int) (int...) (word...)' --- Manually set each replys' weight for each specified word.'")
           
                elif channelMessage[0:24] == '.helpLearn setWeightsAll':
                    reply += str("Usage: '.setWeightsAll (multiple words) (int) (int...)' --- Manually set each reply's weight for all specified words.")
               
                else:
                    reply += str("learn.py commands: .help, .addWord, .addReply, .removeReply, .dictionary, .replies, .wordWeights, .setWeightsIndividual, .setWeightsAll -------- For more info, type '.helpLearn [command]'")
 
            else:
                reply += str("You tried to perform a command, but something went wrong")
       
    else:
        message = channelMessage[len(nick)+2:len(channelMessage)] ### If channel message is not a command, message to jenni starts after a space after the colon ###
        reply += str(processMessage(message)) ### Process the message to determine reply ###
        prevMessage = channelMessage[len(nick)+2:len(channelMessage)] ### Store the channel message for later use ###
    phenny.say(reply)
   
    with open("dictionary.txt", 'w') as inf: ### Write the dictionary to file ###
        inf.write(str(word))
    with open("list_of_replies.txt", 'w') as data: ### Write replies to file ###
        data.write(str(replies))   
 
learn.rule = r'(.*)'
learn.priority = 'high'
 
if __name__ == '__main__':
    print __doc__.string()
