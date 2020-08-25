"""
    Please initialize below variables (select flag - 'YES' / 'NO') based on your needs.
"""

okta_server = os.environ.get('OKTA_URL') # Update Okta tenant https://<yourOrg>.okta.com in .env file
api_token   = os.environ.get('OKTA_API_TOKEN')  # Update your Okta API token in .env file
headers     = {'Content-Type': "application/json",
           'Accept': "application/json", 'Authorization': f"SSWS {api_token}"}

getuser_flag    = 'NO'          # [YES or NO] get users details based on current status
getuser_filter  = 'DEPROVISIONED'
delete_flag     = 'NO'          # [YES or NO] Change to 'YES' to DELETE users
delete_filter   = 'DEPROVISIONED'
activate_flag   = 'NO'          # [YES or NO] Change to 'YES' to ACTIVATE users
activate_filter = '-'
send_activation_email = 'false' # [true or false] Change to 'true' to send email when user activated

group_membership_flag   = 'NO'  # Print User's group membership
okta_userid             = '-'   # Enter Okta User ID to get group membership

getapps_flag            = 'NO'  # list all apps from Okta tenant

list_users_assigned_to_app_flag = 'NO'  # List all users assigned to an App
list_users_assigned_to_app_filter = '-' # Enter AppID


"""
Print Users list in CSV file filter by STATUS
"""

# main() method will check all different flags [YES / NO] from above initialized variables and accordingly invoke a method to perform action.
def main():

    if getuser_flag == 'YES':
        print('\n****************** Listing Users ******************')
        get_users()

    if activate_flag == 'YES':
        print('\n****************** Activating Users ******************')
        activate_users()

    if delete_flag == 'YES':
        print('\n****************** Deleting Users ******************')
        delete_users()

    if group_membership_flag  == 'YES':
        print('\n****************** Get Ggroup Membership ******************')
        get_group_membership()

    if getapps_flag  == 'YES':
        print('\n****************** List all Apps ******************')
        get_apps()

    if list_users_assigned_to_app_flag  == 'YES':
        print('\n****************** List Users Assigned to App ******************')
        list_users_assigned_to_app()


def get_users():
    """Print Users list in CSV file, filter by STATUS (To confirm the users before
    deleting it)"""
    url = f'{okta_server}/api/v1/users?limit=200&filter=status eq "{getuser_filter}"'
    okta_get_resp = requests.get(url, headers=headers)
    csv_file = os.getcwd() + '\Get_Okta_Users.csv'

    if okta_get_resp.status_code > 200:
        print('\nUnable to get response from Okta - get_users(). status_code = ', okta_get_resp)
        raise Exception(okta_get_resp)
    else:
        employee_data = open(csv_file, 'w')
        csvwriter = csv.writer(employee_data, lineterminator='\n')
        print('\nWriting output to ' + csv_file)
        # Write Header in CSV
        csvwriter.writerow(['Okta_ID', 'Status', 'FirstName',
                            'LastName', 'FirmCode', 'Email', 'OktaLogin', 'sAMAccountName']),

        while True:
            for emp in okta_get_resp.json():
                # Write each employee data in a separate row
                csvwriter.writerow([emp.get('id'), emp.get('status'), emp.get('profile').get('firstName'), emp.get('profile').get(
                    'lastName'), emp.get('profile').get('firmCode'), emp.get('profile').get('email'), emp.get('profile').get('login'), emp.get('profile').get('sAMAccountName')])

            # Terminate if next url not found in 'Link' (response header)

            nextLink = okta_get_resp.links.get('next')

            if nextLink is None:
                employee_data.close()
                break

            #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
            elif okta_get_resp.status_code == 429:
                sleep = int(okta_get_resp.headers.get(
                    'X-Rate-Limit-Reset')) - int(time.time())
                print(
                    f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
                time.sleep(5) if sleep < 5 else time.sleep(sleep)

            # Get the nextLink URL and make a request
            else:
                okta_get_resp = requests.get(nextLink['url'], headers=headers)



def activate_users_thread(row):

    """ Activate STAGED users """
    while True:
        # send POST request to Activate each user found by filter
        okta_post_resp = requests.post(row["ActivateUserAPI"], headers=headers)

        #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
        if okta_post_resp.status_code == 429:
            sleep = int(okta_post_resp.headers.get(
                'X-Rate-Limit-Reset')) - int(time.time())
            print(
                f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
            time.sleep(5) if sleep < 5 else time.sleep(sleep)

        # status_code = 200 meaning user activated successfully.
        if okta_post_resp.status_code == 200:
            break

    print(f'\tActivated = {row["FirstName"]} {row["LastName"]}')


def activate_users():
    url = f'{okta_server}/api/v1/users?limit=200&filter=status eq "{activate_filter}"'
    okta_get_resp = requests.get(url, headers=headers)
    csv_file = os.getcwd() + '\Activate_Okta_Users.csv'

    if okta_get_resp.status_code > 200:
        print('\nUnable to get response from Okta - activate_users(). status_code = ', okta_get_resp)
        raise Exception(okta_get_resp)
    else:
        employee_data = open(csv_file, 'w')
        csvwriter = csv.writer(employee_data, lineterminator='\n')
        print('\nWriting to ' + csv_file)
        # Write Header in CSV
        csvwriter.writerow(['Okta_ID', 'Status', 'FirstName',
                            'LastName', 'FirmCode', 'Email', 'OktaLogin', 'sAMAccountName', 'ActivateUserAPI'])

        while True:
            for emp in okta_get_resp.json():
                csvwriter.writerow([emp.get('id'), emp.get('status'), emp.get('profile').get('firstName'), emp.get('profile').get('lastName'),
                    emp.get('profile').get('firmCode'), emp.get('profile').get('email'), emp.get('profile').get('login'),
                    emp.get('profile').get('sAMAccountName'), okta_server + '/api/v1/users/' + emp.get('id') + '/lifecycle/activate?sendEmail=' + send_activation_email])

            # Terminate if next url not found in 'Link' (response header)

            nextLink = okta_get_resp.links.get('next')

            if nextLink is None:
                employee_data.close()
                break

            #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
            elif okta_get_resp.status_code == 429:
                sleep = int(okta_get_resp.headers.get(
                    'X-Rate-Limit-Reset')) - int(time.time())
                print(
                    f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
                time.sleep(5) if sleep < 5 else time.sleep(sleep)

            # Get the nextLink URL and make a request
            else:
                okta_get_resp = requests.get(nextLink['url'], headers=headers)

    # Users Activation starts from here
    with open(csv_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                line_count += 1

            x = threading.Thread(target=activate_users_thread, args=(row,))
            x.start()

            line_count += 1

        if line_count == 0:
            print(f'Total {line_count} users activated successfully')
        else:
            print(f'Total {line_count - 1} users activated successfully')


def delete_users_thread(row):
    """Delete users based on various filters"""
    while True:
        # This operation on a user that hasn't been deactivated causes that user to be deactivated. A second delete operation is required to actually DELETE the user.
        okta_delete_resp = requests.delete(row["DeleteAPI"], headers=headers)

        #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
        if okta_delete_resp.status_code == 429:
            sleep = int(okta_delete_resp.headers.get(
                'X-Rate-Limit-Reset')) - int(time.time())
            print(
                f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
            time.sleep(5) if sleep < 5 else time.sleep(sleep)

        # status_code = 404 meaning user id not found. (user deleted successfully)
        if okta_delete_resp.status_code == 404:
            break

        # status_code = 400 meaning cannot delete Technical contact for the Org.
        # status_code = 403 meaning cannot delete Okta Org Admin.
        if okta_delete_resp.status_code in [400, 403]:
            print(f'Cannot delete Okta Org Admin user {row["FirstName"]} {row["LastName"]} {okta_delete_resp.text}')
            break

    print(f'\tDeleted = {row["FirstName"]} {row["LastName"]}')


def delete_users():
    url = f'{okta_server}/api/v1/users?limit=200&filter=status eq "{delete_filter}"'
    okta_get_resp = requests.get(url, headers=headers)
    csv_file = os.getcwd() + '\Delete_Okta_Users.csv'

    if okta_get_resp.status_code > 200:
        print('\nUnable to get response from Okta - delete_users(). status_code = ', okta_get_resp)
        raise Exception(okta_get_resp)
    else:
        employee_data = open(csv_file, 'w')
        csvwriter = csv.writer(employee_data, lineterminator='\n')
        print('\nWriting output to ' + csv_file)
        # Write Header in CSV
        csvwriter.writerow(['Okta_ID', 'Status', 'FirstName',
                            'LastName', 'FirmCode', 'Email', 'OktaLogin', 'sAMAccountName', 'DeleteAPI'])
        while True:
            for emp in okta_get_resp.json():
                # Write each employee data in a separate row
                csvwriter.writerow([emp.get('id'), emp.get('status'), emp.get('profile').get('firstName'), emp.get('profile').get(
                    'lastName'), emp.get('profile').get('firmCode'), emp.get('profile').get('email'), emp.get('profile').get('login'), emp.get('profile').get('sAMAccountName'), okta_server + '/api/v1/users/' +
                    emp.get('id') + '?sendEmail=false'])

            # Terminate if next url not found in 'Link' (response header)

            nextLink = okta_get_resp.links.get('next')

            if nextLink is None:
                employee_data.close()
                break

            #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
            elif okta_get_resp.status_code == 429:
                sleep = int(okta_get_resp.headers.get(
                    'X-Rate-Limit-Reset')) - int(time.time())
                print(
                    f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
                time.sleep(5) if sleep < 5 else time.sleep(sleep)

            # Get the nextLink URL and make a request
            else:
                okta_get_resp = requests.get(nextLink['url'], headers=headers)

    # Delete users starts from here
    with open(csv_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0

        for row in csv_reader:
            if line_count == 0:
                line_count += 1

            x = threading.Thread(target=delete_users_thread, args=(row,))
            x.start()

            line_count += 1
        if line_count == 0:
            print(f'Total {line_count} users deleted successfully')
        else:
            print(f'Total {line_count - 1} users deleted successfully')

def get_group_membership():
    """Print Users group membership"""
    url = f'{okta_server}/api/v1/users/{okta_userid}/groups'
    okta_get_resp = requests.get(url, headers=headers)
    csv_file = os.getcwd() + '\Get_Okta_Group_Membership.csv'

    if okta_get_resp.status_code > 200:
        print('\nUnable to get response from Okta - get_group_membership(). status_code = ', okta_get_resp)
        raise Exception(okta_get_resp)
    else:
        group_data = open(csv_file, 'w')
        csvwriter = csv.writer(group_data, lineterminator='\n')
        print('\nWriting output to ' + csv_file)
        # Write Header in CSV
        csvwriter.writerow(['OktaGroupID', 'GroupType', 'GroupName', 'GroupDescription', 'groupType', 'GroupAMAccountName', 'groupDN']),

        while True:
            for grp in okta_get_resp.json():
                # Write each employee data in a separate row
                csvwriter.writerow([grp.get('id'), grp.get('type'), grp.get('profile').get('name'), grp.get('profile').get(
                    'description'), grp.get('profile').get('groupType'), grp.get('profile').get('samAccountName'), grp.get('profile').get('dn')])

            # Terminate if next url not found in 'Link' (response header)

            nextLink = okta_get_resp.links.get('next')

            if nextLink is None:
                group_data.close()
                break

            #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
            elif okta_get_resp.status_code == 429:
                sleep = int(okta_get_resp.headers.get(
                    'X-Rate-Limit-Reset')) - int(time.time())
                print(
                    f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
                time.sleep(5) if sleep < 5 else time.sleep(sleep)

            # Get the nextLink URL and make a request
            else:
                okta_get_resp = requests.get(nextLink['url'], headers=headers)


def get_apps():
    """List Apps"""
    url = f'{okta_server}/api/v1/apps'
    okta_get_resp = requests.get(url, headers=headers)
    csv_file = os.getcwd() + '\Okta_Apps.csv'

    if okta_get_resp.status_code > 200:
        print('\nUnable to get response from Okta - get_apps(). status_code = ', okta_get_resp)
        raise Exception(okta_get_resp)
    else:
        apps_data = open(csv_file, 'w')
        csvwriter = csv.writer(apps_data, lineterminator='\n')
        print('\nWriting output to ' + csv_file)
        # Write Header in CSV
        csvwriter.writerow(['Name', 'Label' , 'Status','Username_Format', 'Complete JSON']),

        while True:
            for apps in okta_get_resp.json():
                # Write each employee data in a separate row
                csvwriter.writerow([apps.get('name'), apps.get('label'), apps.get('status'), apps.get('credentials').get('userNameTemplate').get('template'), apps.get('credentials')])
                # csvwriter.writerow([apps])

            # Terminate if next url not found in 'Link' (response header)

            nextLink = okta_get_resp.links.get('next')

            if nextLink is None:
                apps_data.close()
                break

            #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
            elif okta_get_resp.status_code == 429:
                sleep = int(okta_get_resp.headers.get(
                    'X-Rate-Limit-Reset')) - int(time.time())
                print(
                    f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
                time.sleep(5) if sleep < 5 else time.sleep(sleep)

            # Get the nextLink URL and make a request
            else:
                okta_get_resp = requests.get(nextLink['url'], headers=headers)


def list_users_assigned_to_app():
    """ List Users Assigned to App """
    url = f'{okta_server}/api/v1/apps/{list_users_assigned_to_app_filter}/users'
    okta_get_resp = requests.get(url, headers=headers)
    csv_file = os.getcwd() + '\List_Users_Assigned_to_App.csv'

    if okta_get_resp.status_code > 200:
        print('\nUnable to get response from Okta - list_users_assigned_to_app_flag(). status_code = ', okta_get_resp)
        raise Exception(okta_get_resp)
    else:
        apps_data = open(csv_file, 'w')
        csvwriter = csv.writer(apps_data, lineterminator='\n')
        print('\nWriting output to ' + csv_file)
        # Write Header in CSV
        csvwriter.writerow(['Okta_User_ID', 'lastUpdated', 'userName']),

        while True:
            for users in okta_get_resp.json():
                # Write each employee data in a separate row
                csvwriter.writerow([users.get('id'), users.get('lastUpdated'), users.get('credentials').get('userName')])

            # Terminate if next url not found in 'Link' (response header)

            nextLink = okta_get_resp.links.get('next')

            if nextLink is None:
                apps_data.close()
                break

            #  status_code = 429 meaning Rate-Limit exceed. this might not delete user. Waiting until okta reset rate limit.
            elif okta_get_resp.status_code == 429:
                sleep = int(okta_get_resp.headers.get(
                    'X-Rate-Limit-Reset')) - int(time.time())
                print(
                    f'Waiting to reset X-Rate-Limit-Reset, Sleeping for {sleep} seconds')
                time.sleep(5) if sleep < 5 else time.sleep(sleep)

            # Get the nextLink URL and make a request
            else:
                okta_get_resp = requests.get(nextLink['url'], headers=headers)



main()
