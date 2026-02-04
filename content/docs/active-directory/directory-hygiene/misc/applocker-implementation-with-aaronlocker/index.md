---
title: "AppLocker Implementation with AaronLocker"
date: 2026-02-03T08:51:11
draft: false
authors: ["ahmed"]
weight: 200
tags: ["Hardening", "applocker"]
---
This guide details the step-by-step process of implementing AppLocker in a Windows Active Directory environment using the **AaronLocker** toolset. AaronLocker simplifies the creation and maintenance of AppLocker policies, focusing on a strategy that allows execution from secure (admin-writable) directories while restricting execution from user-writable locations.

## Prerequisites

Before starting, ensure the following requirements are met:

*   **Supported OS:** Windows 7/Server 2008 R2 or later.
*   **PowerShell:** Version 5.0 or later on the management workstation.
*   **Administrative Access:** Domain Admin rights to configure Group Policy and local admin rights on the management workstation.
*   **Sysinternals AccessChk:** Required by AaronLocker to scan for user-writable directories.

## Step 1: Download and Prepare AaronLocker

1.  **Download:** Clone or download the repository from [GitHub](https://github.com/microsoft/AaronLocker).
2.  **Unblock:** If you downloaded a ZIP file, right-click it, select **Properties**, and check **Unblock** before extracting.
3.  **Extract:** Extract the contents to a folder on your management workstation (e.g., `C:\AaronLocker`).
4.  **AccessChk:** Download `accesschk.exe` (and `accesschk64.exe`) from the [Sysinternals website](https://learn.microsoft.com/en-us/sysinternals/downloads/accesschk) and place them in the root of the `C:\AaronLocker` folder.

## Step 2: Customization (The "Audit" Preparation)

AaronLocker works by generating policies based on input scripts found in the `CustomizationInputs` directory. You typically don't edit the logic scripts, only the inputs.

Navigate to `C:\AaronLocker\CustomizationInputs` and review the following:

### 1. TrustedSigners.ps1
Add digital signatures for software that must run from non-standard locations or needs explicit trust.
*   *Example:* If you have internal software signed by a corporate certificate, add the subject name or thumbprint here.

### 2. GetSafePathsToAllow.ps1
Define directories that are **secure** (not user-writable) where executables should be allowed to run.
*   Defaults usually include `%WINDIR%` and `%PROGRAMFILES%`
*   **Crucial:** Ensure these paths are actually secure. If a standard user can write to a folder allowed here, they can bypass AppLocker.

### 3. UnsafePathsToBuildRulesFor.ps1
Define directories that are **user-writable** (unsafe) but contain specific applications that *must* run.
*   AaronLocker will scan these paths and create specific rules (Hash or Publisher) to allow *only* the existing files.
*   *Example:* `C:\Users\*\AppData\Local\WebEx\*`

## Step 3: Scan and Generate Policies

1.  Open **PowerShell** as Administrator.
2.  Navigate to the AaronLocker directory:
    ```powershell
    cd C:\AaronLocker
    ```
3.  (Optional) If you need to find user-writable directories to assess risk, run:
    ```powershell
    .\Scan-Directories.ps1
    ```
4.  **Generate the Policies:**
    Run the creation script. This will compile your inputs into AppLocker XML policy files.
    ```powershell
    .\Create-Policies.ps1
    ```
    *   This usually takes a few minutes.
    *   Output files are saved to the `Outputs` directory.

## Step 4: Deploy in Audit Mode

**Always** start with Audit Mode to assess the impact without breaking business processes.

1.  **Open Group Policy Management** (`gpmc.msc`).
2.  Create a new GPO (e.g., `AppLocker - Audit Mode`) and link it to a test OU containing computer objects.
3.  **Enable the Application Identity Service:**
    *   Navigate to: **Computer Configuration > Policies > Windows Settings > Security Settings > System Services**.
    *   Find **Application Identity**, double-click it, select **Define this policy setting**, and set it to **Automatic**.
4.  **Import the Policy:**
    *   Navigate to: **Computer Configuration > Policies > Windows Settings > Security Settings > Application Control Policies > AppLocker**.
    *   Right-click **AppLocker** and select **Import Policy...**
    *   Browse to `C:\AaronLocker\Outputs` and select the **Audit** version of the policy (e.g., `AaronLockerPolicies_Audit.xml`).
    *   *Note:* Ensure the filename indicates "Audit". AaronLocker generates both Audit and Enforce versions.
5.  **Force Update:** Run `gpupdate /force` on the target client machines or reboot them.

## Step 5: Monitor and Refine

1.  **Collect Logs:**
    *   AppLocker logs are located in Event Viewer under: **Applications and Services Logs > Microsoft > Windows > AppLocker**.
    *   Look for **8003** (EXE) and **8004** (Script) warning events. These indicate what *would* have been blocked.
2.  **Analyze:**
    *   Use the `Collect-AppLockerEvents.ps1` script (provided below) or similar log forwarding tools to aggregate these logs.
    *   Identify legitimate business applications that are appearing in the logs.
3.  **Update Rules:**
    *   Go back to **Step 2** and modify the scripts in `CustomizationInputs`.
    *   If a specific signed app was blocked, add its publisher to `TrustedSigners.ps1`.
    *   If a static path was blocked, add it to `UnsafePathsToBuildRulesFor.ps1` (if user-writable) or `GetSafePathsToAllow.ps1` (if secure).
    *   **Re-run** `Create-Policies.ps1` to generate new XML files.
    *   **Re-import** the updated Audit policy into the GPO.

### PowerShell Script to Collect AppLocker Audit Events

To aid in monitoring, use the following PowerShell script to collect and summarize AppLocker audit events (Event IDs 8003 and 8004) to a CSV file.

```powershell
<#
.SYNOPSIS
    Collects AppLocker Audit events (8003 & 8004) and exports a summary to CSV.

.DESCRIPTION
    This script queries the local 'Microsoft-Windows-AppLocker/EXE and DLL' and 
    'Microsoft-Windows-AppLocker/MSI and Script' event logs for events 8003 (EXE Audit) 
    and 8004 (Script/MSI Audit). It parses the XML data to extract the FilePath, 
    User, and Rule information, then exports the results to a CSV file.

.NOTES
    Event 8003: Allowed but would have been prevented (EXE/DLL)
    Event 8004: Allowed but would have been prevented (Script/MSI)
#>

$OutputCsv = ".\AppLocker_Audit_Summary.csv"
$LogNames = @('Microsoft-Windows-AppLocker/EXE and DLL', 'Microsoft-Windows-AppLocker/MSI and Script')

Write-Host "Querying AppLocker logs for Audit events (8003, 8004)..." -ForegroundColor Cyan

try {
    $Events = Get-WinEvent -FilterHashTable @{
        LogName = $LogNames
        ID      = 8003, 8004
    } -ErrorAction Stop
}
catch {
    Write-Warning "No AppLocker audit events found or unable to query logs."
    Write-Warning $_.Exception.Message
    exit
}

$Results = New-Object System.Collections.Generic.List[PSCustomObject]

foreach ($Event in $Events) {
    # Convert to XML for reliable property extraction
    $Xml = [xml]$Event.ToXml()
    $Data = $Xml.Event.EventData.Data

    # Extract fields based on the 'Name' attribute in the EventData XML
    $FilePath   = ($Data | Where-Object { $_.Name -eq "FilePath" }).'#text'
    $RuleName   = ($Data | Where-Object { $_.Name -eq "RuleName" }).'#text'
    $TargetUser = ($Data | Where-Object { $_.Name -eq "TargetUser" }).'#text'
    $PolicyName = ($Data | Where-Object { $_.Name -eq "PolicyName" }).'#text'

    # Resolve SID to Username if possible, otherwise keep SID
    try {
        $UserObj = New-Object System.Security.Principal.SecurityIdentifier($TargetUser)
        $UserName = $UserObj.Translate([System.Security.Principal.NTAccount]).Value
    }
    catch {
        $UserName = $TargetUser
    }

    $Results.Add([PSCustomObject]@{
        TimeCreated = $Event.TimeCreated
        EventID     = $Event.Id
        Type        = if ($Event.Id -eq 8003) { "EXE/DLL" } else { "Script/MSI" }
        Computer    = $Event.MachineName
        User        = $UserName
        FilePath    = $FilePath
        RuleName    = $RuleName
        PolicyName  = $PolicyName
    })
}

# Export to CSV
$Results | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding UTF8

Write-Host "Successfully exported $($Results.Count) events to $OutputCsv" -ForegroundColor Green
Write-Host "You can open this file in Excel to analyze which applications need to be whitelisted." -ForegroundColor Gray
```

## Step 6: Switch to Enforce Mode

Once the Audit logs show no legitimate applications being blocked (clean logs):

1.  Open the Group Policy Management Editor for your AppLocker GPO.
2.  Navigate to the AppLocker settings.
3.  Right-click **AppLocker** and select **Import Policy...**
4.  Select the **Enforce** version of the policy from the `Outputs` folder (e.g., `AaronLockerPolicies_Enforce.xml`).
5.  (Optional but recommended) Rename the GPO to `AppLocker - Enforced`.
6.  Monitor closely for the first few days.

## Maintenance

*   **New Software:** When deploying new software, determine if it falls under existing allowed paths or publishers. If not, update the AaronLocker inputs, regenerate policies, and update the GPO *before* rolling out the software.
*   **Regular Audits:** Periodically review the `UnsafePathsToBuildRulesFor` list to ensure it hasn't grown too permissive.
