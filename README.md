# What is this repository

Welcome to `decal-attend`. This is a gradescope autograder that allows us to sync our Google Forms attendance results with a gradescope assignment throughout the semester.

# How does it work?

The autograder is provisioned on Gradescope's server by creating a zip of the contents in the `autograder-zip` folder (alongside a public and private key; see the instructions below). The autograder's setup script establishes a local clone of this repository on the server and then checks out the branch relevant to this semester. In this branch, there must be the autograder files configured for this semester. Whenever the autograder runs, it will fetch the latest code from GitHub, and then fetch the current attendance sheets from Google's API. The latest code is ran on these sheets to produce the final output.

One upside of this approach is that any updates made to `run_tests.py` or `utils.py` do not require the autograder to be reprovisioned - only changes to files in the `autograder-zip` folder require reprovisioning.

# Setting up the Autograder

First, create an attendance sheet (Make a copy of the current attendance form at [hkn.mu/decal-attend](https://hkn.mu/decal.attend)). Then, make a new Google Sheets file with the Form Responses attached. In that Google Sheet, copy exactly the contents of the keywords, Email Map, and responses sheet (in that order) from [this sheet](https://docs.google.com/spreadsheets/d/1NZFt_ZgkvujTZaKIsiY_mNkP-ixJUOkRPyUBogQZaRY/edit?gid=1457747331#gid=1457747331). Clear the email mappings from the Email Map tab.

Now, we have to create a Google Service Account. Navigate to [the service worker page in Google Cloud Platform](https://console.cloud.google.com/iam-admin/serviceaccounts), and make sure you're logged in to your HKN account. Ask an IP Decal Officer to be added to the Decal Attendance Tracker project (if no officer is available, it should be fine to make a new project). Select your project, then press "Create Service Account". Name the account `[FA/SP]XX Decal Attendance Tracker`, then press create and continue. You can continue through the other fields, they are not important. Click on the new service worker in the table, and navigate to the Keys tab. Add a JSON key, and download it. Save this for later. Finally, copy the email address of your service account (which is in the main table on the Service Accounts page) and share the attendance sheet with this email. Your Google backend is now set up.

Next, you have to set up the Gradescope autograder. Clone this repository on to your local machine. Modify line 19 of `setup.sh` to check out a branch corresponding to the current semester. You will make this branch later. Now we have to create a SSH key for the server. In this project's root directory, run `ssh-keygen`. When prompted, say that you would like to save the key in `/autograder-zip/deploy_key`. This will create `deploy_key` and `deploy_key.pub` in your `autograder-zip`. Also copy over the JSON file you downloaded earlier while making a Service Account into `autograder-zip`, and rename it to `secret.json`.

Back on Github, navigate to your repository settings and select Deploy Keys. Press `Add a deploy key`, and name it `[FA/SP]XX Autograder`. Into the Key box, copy the contents of `deploy_key.pub`, and press Add key. **Do not give the key write access.**

You can now create your autograder zip by zipping everything in `autograder-zip`. **Be careful not to push this zip file, your deploy_key, or your secret.json to Github**, but remember to push the change in semester.

Next, create a branch on your local machine named `[fa/sp]XX`. In this branch, remove autograder-zip (be careful not to delete your `deploy_key`), and open `run_tests.py`. In this file, modify the SEMESTER_CONFIG object to have the right sheet id and gids for your project (These can be found in the URL of your Google sheet - the sheet_id is the one after `/d` and before `/edit`, and the `gid` for each sheet will be appended on to the end of the URL when you click on the resources and keywords sheets respectively). Push your changes.

You are now ready to add the autograder to Gradescope. Create a new programming assignment called "Decal Attendance", and set the number of points to the number of lectures in the semester. Set the assigned date to the first day you'd like the students to see the assignment, and set the due date to the last date in the semester. Once the assignment is created, it will ask you for an autograder file. Here, you should upload your zip file. Now, in order for students to see their grades, you must either create a submission for each of them or ask each of them to create a submission on their own. **The content of this submission does not matter - it is disregarded.** Gradescope just requires a submission for the autograder to run. For fa24, I uploaded a file called `autograder` that was entirely empty for each student.

The autograder is now up and running!

# Using the Autograder

## Adding a lecture / Setting a keyword?

This can be done in the Google Sheet directly. In the keywords tab, all values in the Lecture column will be treated as individual tests. If a date surrounded by parentheses `(MM/YY)` is included in the Lecture title, this information will be used to hide lectures that have not yet passed from the student-facing submission. Whatever is placed into the "Secret Word" tab will be used to validate the Secret Word by the autograder. Note that this is case insensitive, and that whitespace will be trimmed from student responses before checking.

## Resolving inconsistencies

If a student filled out the form with an email that was not their gradescope email, the Email Map tab in the Google Sheet can be used. Any emails placed into the "Input Email" column will be mapped to the corresponding email in the "Gradescope Email" column in the `responses` sheet.

## How do I refresh the autograder?

Open the attendance Google Sheet and download the `responses` and `keywords` tabs as `.csv` files. Rename these files to `responses.csv` and `keywords.csv` respectively, then replace the `responses.csv` and `keywords.csv` files currently found in your semester branch. Push your changes to GitHub.

In Gradescope, navigate to the Decal Attendance assignment and go to the Manage Submissions tab. Press "Regrade All Submissions" in the bottom left, then press "Regrade" in the modal that appears. These new sheets will be pulled and each students' grades will be updated.
