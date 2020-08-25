# Okta User Lifecycle Management and other essentials operation via Okta API

===== Okta_UserLifeCycle_API.py =====

This code can perform below Okta operations and write output to csv file.

    DELETE USERS IN BULK.
    ACTIVATE USERS IN BULK.
    FETCH USERS FILTER BY CURRENT STATUS.
    FETCH USER'S GROUP MEMBERSHIP.
    LIST ALL APPS FROM OKTA TENANT.
    LIST ALL USERS ASSIGNED TO AN APP.

This code uses multi-threading to furiously delete and activate the Okta users.

Please update the environment variables in a file named '.env' as below:
    OKTA_URL=[https://<>.okta.com]
    OKTA_API_TOKEN=[Use your API Token which has Admin privilege]

    ###################################### IMPORTANT ####################################################
    #                                                                                                   #
    # Please initialize the variables as per your requirement:                                          #
    #                                                                                                   #
    #    delete_flag     =[YES | NO]  Change to 'YES' to DELETE users                                   #
    #    getuser_flag    =[YES | NO]  get users details based on current status                         #
    #    activate_flag   =[YES | NO]  Change to 'YES' to ACTIVATE users                                 #
    #    delete_filter   =[DEPROVISIONED (Deactivated) | PROVISIONED | SUSPENDED | STAGED | ACTIVE]     #
    #                     (Delete users based on its current status.)                                   #
    #    getuser_filter  =[DEPROVISIONED (Deactivated) | PROVISIONED | SUSPENDED | STAGED | ACTIVE]     #
    #                     (to list all Staged users before deleting or activating users)                #
    #    activate_filter =[STAGED] (to activate all Staged users)                                       #
    #    send_activation_email = [true | false]                                                         #
    #                     (Change to 'true' to send email when user activated)                          #
    #    group_membership_flag   =[YES | NO]  Print User's group membership                             #
    #    okta_userid             =[USER ID]   Enter Okta User ID to get group membership                #
    #    getapps_flag            =[YES | NO]  list all apps from Okta tenant                            #
    #    list_users_assigned_to_app_flag =[YES | NO]  List all users assigned to an App                 #
    #   list_users_assigned_to_app_filter =[APP ID] Enter AppID.                                        #
    #                    (when you access select app in Admin console, you can see APP ID in the URL)   #
    #                                                                                                   #
    #####################################################################################################

    Developed By : Vipul Kaneriya
