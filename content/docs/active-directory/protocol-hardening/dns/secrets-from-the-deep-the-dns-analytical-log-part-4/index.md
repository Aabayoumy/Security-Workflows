---
title: "Secrets from the Deep – The DNS Analytical Log – Part 4"
date: 2026-02-03T08:52:24
draft: false
authors: ["ahmed"]
weight: 200
tags: ["DNS"]
---
Hi Team, it's Eric Jansen again, here today to continue where we left off in [Part 3](https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/secrets-from-the-deep-the-dns-analytical-log-part-3/ba-p/1985830) of the series.  In the last episode, we discussed how to parse the DNS Analytical Log using a sample scenario where I've deployed a DNS Black Hole Solution, and my goal was to harvest specific data of interest.  Today we are going to take the data that we previously collected and report our findings.  I wanted to talk about this because I've seen a number of customers employ DNS block lists as a security measure, but they don't look to see what's getting blocked, which I find somewhat shocking.  If you don’t check to see what's actually being blocked, other than the occasional end user complaining that they can’t get to something, how would you know if the block list is providing any value at all? 

There are many ways to report the data of interest but today I'm going to show a simple means to do some basic reporting, writing just the data that you care about, to its own event log.  We'll take the millions of events that we parsed through in the last part of this series and simply report the findings in just a handful of 'higher level' (arguably more useful) events, while still giving you the ability to find any of the more specific data that you're interested in.   

**Note:** For the ease of discussion, I'm taking small snips of code from a much larger function that I've written (where additional events are parsed) and showing just the necessary info in the code blocks below for ease of discussion.  In some cases, I'm changing the code from the function so that it makes more sense when seen independently.  Towards the end of this series, I'll likely post all of the complete functions to a GitHub repository for folks to use. 

And with that, here’s the usual disclaimer that all my code samples come with: 

The code snippets above are considered sample scripts.  Sample scripts are not supported under any Microsoft standard support program or service. The sample scripts are provided AS IS without warranty of any kind. Microsoft further disclaims all implied warranties including, without limitation, any implied warranties of merchantability or of fitness for a particular purpose. The entire risk arising out of the use or performance of the sample scripts and documentation remains with you. In no event shall Microsoft, its authors, or anyone else involved in the creation, production, or delivery of the scripts be liable for any damages whatsoever (including, without limitation, damages for loss of business profits, business interruption, loss of business information, or other pecuniary loss) arising out of the use of or inability to use the sample scripts or documentation, even if Microsoft has been advised of the possibility of such damages. 

Ok, so in the last episode, we ran some snippets of code, which resulted in data being stored in a variable called **$****HitData**.  That variable contained query data that was blocked by the server as a result of DNS policy.  The first thing that we're going to do is create a new event log to put this 'data of interest' into: 

```
#Create custom Event Log for parsed DNS Analytic data.

$CustomEventlogName = "DNS-Server-AnalyticLog-ParseData"
$EventSource_PAL = "Parse-AnalyticLog"
$EventSource_DD = "DENIED_Domains"
New-EventLog -LogName $CustomEventlogName -Source $EventSource_PAL,$EventSource_DD
```

The snippet above creates a new Event log called ***DNS-Server-******AnalyticLog******\-******ParseData***, defining two event sources, that we'll be using later on.  Our mission now is to extract that data into even more 'boiled down' higher level info.  To do that we're going to pick and choose the data that we want out of **$****HitData** for building messages to write to our shiny new custom event log.  Here's a sample of how we can get that done: 

```
#If hits are found, process them.
If($HitData){

    #Defines the a .csv log file path for ALL hit data to be dumped to. Ideally this would be ingested into SQL.
    $CSVLogFilePath = "D:\Logs\$($ENV:COMPUTERNAME)_BHDomainHits_$(Get-Date -Format "ddMMMyyyy_HHmm").csv"

    $HitData | sort timestamp | Export-Csv $CSVLogFilePath -NoTypeInformation        

    #Variable containing the higher level information of interest.
    $Message += "The HitData has been sorted and dumped to $($CSVLogFilePath).`n" | Out-String
      
    #Collect QRP Count for use in calculating the percentage of blocked domains that are hit.
    $QRPCount = (Get-item 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\DNS Server\Policies').SubKeyCount

    #Sorts EventID 258 data.
    $258HitData = $HitData | where EventID -eq 258
    $Unique258Queries = $258HitData | sort XID -Unique | select -ExpandProperty XID
    $Unique258Domains = $258HitData | sort Query -Unique | select -ExpandProperty Query
    $Unique258QuerySources = $258HitData | sort QuerySource -Unique| select QuerySource
    
    $UQCount = $Unique258Queries.count
    $UDCount = $Unique258Domains.count
    $UQSCount = $Unique258QuerySources.count
                        
    #If there are 258 events that were a result of 'Policy', the 'high level' findings breakdown is output to the DNS-Server-AnalyticLog-ParseData event log, in event ID 2.
    $Message += "There were $($j) RESPONSE_FAILURE events; out of those there were $l that were not a result of a Query Resolution Policy match." | Out-String
    $Message += "Out of those $($j) events, $($UQCount) were unique, based on the Transaction ID (XID)." | Out-String
    $Message += "The $($UQCount) unique queries originated from $() clients, and boiled down to $($UDCount) unique domains queried.`n" | Out-String
    $Message += "The $($UQSCount) clients are:" | Out-String
    $Message += $($Unique258QuerySources) | sort QuerySource -Descending | Format-Wide -Property QuerySource -Column 5 | Out-String  
    $Message += "This represents $($($UDCount/$QRPCount)*100) percent of what's being blocked via the $($QRPCount) QRPs." | Out-String
    $Message += "The corresponding Domains that were flagged as Policy Hits and DENIED can be found in Event ID 3.`n" | Out-String
            
    If($Unique258Domains){
               
        #The -Message parameter for Write-EventLog allows a maximum of 32766 characters, so the data within must be within those limits.
        If($(Get-CharacterCount -InputObject $Unique258Domains) -lt 32500){
        
        #Response Failure Domain Message Data.
        $RFMessage = "Black Hole Domain Hits - DENIED Domains:`n" | Out-String
        $RFMessage += $Unique258Domains | Out-String

        #Domains that were blocked are output to the DNS-Server-AnalyticLog-ParseData event log as it's own event, in event ID 3.
        Write-EventLog -LogName $CustomEventlogName -Source $EventSource_DD -EventId 3 -Message $RFMessage
        }
        Else{
        $CharLength = $(Get-CharacterCount -InputObject $Unique258Domains)
        Write-Warning "The character limit for the maximum allowable size of the message within for the Event ID has been exceeded and has a length of $($CharLength), but only 32766 characters are allowed."
        Write-Host "`nPrinting the DENIED Domains to the screen instead:`n"
        $Unique258Domains
        }
    }

    #Send the data of interest to the DNS-Server-AnalyticLog-ParseData event log located in "Application and Services Logs".
    Write-EventLog -LogName $CustomEventlogName -Source $EventSource_PAL -EventId 2 -Message $Message

    #Find the last event to be parsed and output it to the DNS-Server-AnalyticLog-ParseData event log located in "Application and Services Logs".
    Write-EventLog -LogName $CustomEventlogName -EventId 1 -Source $EventSource_PAL -Message "LastIterationLastEventTimeStamp - $($LastEventTimestamp)"            
}
Else{
$WarningMsg = "There was no hit data found. This could be a good news or due to one of the following scenarios - but this is by no means an all inclusive list:"
$NoHitsMessage = $WarningMsg | Out-String
$NoHitsMessage += "`n"
$NoHitsMessage += " - The Parse-DNSAnalyticLog function was run without elevated credentials (The account didn't have permissions to the log to be able to parse it)." | Out-String
$NoHitsMessage += " - The DNS analytic log was just recently cleared." | Out-String
$NoHitsMessage += "`t This is usually due to a reboot, but it could have also been administratively done." | Out-String
$NoHitsMessage += " - The DNS analytic log was just recently turned on." | Out-String            
$NoHitsMessage += " - There are no Query Resolution Policies on the server." | Out-String
$NoHitsMessage += " - If there are Query Resolution Policies, then they could be Disabled. Check the Policies to see if they're disabled { Get-DNSServerQueryResolutionPolicy }." | Out-String
$NoHitsMessage += " - If there are Query Resolution Policies, then they could be getting Ignored. Check the DNS Server Settings { (Get-DNSServerSetting -All).IgnoreServerLevelPolicies }." | Out-String
$NoHitsMessage += " - The inbound queries aren't meeting the criteria defined within the Query Resolution Policies." | Out-String

Write-Warning $WarningMsg
$NoHitsMessage.Substring($($WarningMsg.Length + 2))
Write-EventLog -LogName $CustomEventlogName -Source $EventSource_PAL -EventId 0 -Message $NoHitsMessage
}
```

In the code above, you'll notice a non-native function called **Get-CharacterCount**, that can be found here:

```
function Get-CharacterCount ([String]$InputObject)
{
    $($InputObject | Measure-Object -Character).Characters
}
```

I have notes in the code, but in summary, it further picks apart the data that's stored in the **$****HitData** variable and stores it into separate variables for use in building possible messages that are dumped to the different events.  For this scenario, I have four Events defined: 

**Event ID 0** - This event is triggered if a parsing cycle occurs and there are not hits, which is possible, but unlikely (depending on the block list used).  This lists possible reasons for this event being triggered. 

**Event ID 1** - This event is triggered on every parsing cycle, but only if events are found in the **$****HitData** variable.  In this case it logs the timestamp of the last event that was parsed, during the last parsing iteration. 

**Event ID 2** - This event shows the "Bottom-Line Up-Front" information that can be customized to whatever you decide is of value. 

**Event ID 3** - This event shows just the domains that were Denied from query attempts to the resolver.  The list tends to be long, so I have it stored as its own event. 

One thing to consider, in [Part 3](https://techcommunity.microsoft.com/t5/core-infrastructure-and-security/secrets-from-the-deep-the-dns-analytical-log-part-3/ba-p/1985830) of the series, I show how to build a hash table for use in filtering the log for just the 258 events, but you can add more filters to that to further reduce the amount of data that needs to get parsed.  That's the reason that I've included Event ID 1 above - when employed, it tells the next parse attempt to start parsing events beginning when the last event that was parsed.  This can save a considerable amount of time, depending on traffic and how long you go between parsing cycles, among other things.  The snippet below shows how I collect the timestamp and how to use it in the **$****FilterHashTable** variable - essentially, just adding to that which I previously showed: 

```
#Tries to collect the LastIterationLastEventTimeStamp value from the latest Event ID 1. 

IF( $((Get-EventLog $CustomEventlogName -Newest 1 -InstanceId 1 -ErrorAction SilentlyContinue).message.split('-').trim()[1]) ){

#If there is, I store the content in a variable as a datetime format so that I can start the event search looking for events after the last parsed timestamp.

    $LastIterationLastEventTimeStamp = Get-Date $((Get-EventLog $CustomEventlogName -Newest 1 -InstanceId 1 -ErrorAction SilentlyContinue).message.split('-').trim()[1])

}
```

The updated Hash Table would just include a new value - StartTime:

```
#Build the HashTable for use with Get-WinEvent

$FilterHashTable = @{
Path=$DNSAnalyticalLogPath
ID=$EventIDs
StartTime= $LastIterationLastEventTimeStamp
}  
```

At this point, we've further parsed the collected data into subsets of information for building messages for writing to our custom event log, showing only the "Bottom\-Line Up\-Front" information that we're interested in.  At the same time however, we're writing ALL hit data to a .csv file during each parsing cycle, so we still have the ability to further investigate any interesting information that we find in the new events that we're writing to.  We have the best of both worlds!  The .csv files (I say plural, because ideally this parser would be set up to run on a schedule) can further be leveraged by ingesting them into SQL or other data repositories for use in analyzing historical trends among other metrics.  So let's take a look at what I have in my lab, to show you what the final product looks like in Event ID Order:

|   **Event ID 0:**    |   **Possible explanations** **of why there are no Query Resolution Policy hits.**    |
| --- | --- |

I didn't have any examples of this event, so I had to reproduce it artificially to be able to get a screenshot of it: 

|   **Event ID 1:**    |   **Timestamp of the last event that was parsed during the last parsing cycle.**     |
| --- | --- |

|   **Event ID 2:**    |   **Bottom-Line Up-Front** **Data - This can be whatever you think is** **im****portant.**    |
| --- | --- |

|   **Event ID 3:**    |   **List of domains that were blocked** **as a result of** **a Query Resolution Policy.**    |
| --- | --- |

Well, team...as you can see, we've managed to successfully parse the DNS Analytic Log, define some data of interest, and then built some report data that we've shipped to a custom created event log called ***DNS-Server-******AnalyticLog******\-******ParseData****.*  It's not the prettiest solution, and there's plenty of room for innovation, but it's better than just putting a block list in place and not knowing if it's effective or not.  Now you just need to remember to check the logs, like any other log that you deem important. 

You know what would be super cool though??  What if instead of just shipping this data to an event log, what if we were able to use PowerBI to give us some visuals of this data that we deemed important?  Maybe some charts and graphs showing important data on a per resolver basis.  That'd be pretty cool.

Until next time!
