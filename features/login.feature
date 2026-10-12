Feature: Login
  As a registered user of Swag Labs
  I want to log in with my credentials
  So that I can access the product inventory

  Scenario: Successful login with valid credentials
    Given I am on the login page
    When I log in as "standard_user" with password "secret_sauce"
    Then I should land on the inventory page

  Scenario: Locked out user is rejected
    Given I am on the login page
    When I log in as "locked_out_user" with password "secret_sauce"
    Then I should see the error "Sorry, this user has been locked out"