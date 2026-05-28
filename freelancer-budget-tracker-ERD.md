# Freelancer Budget Tracker - ERD

This document outlines the Entity-Relationship Diagram (ERD) for the Freelancer Budget Tracker application. The ERD illustrates the relationships between the application's entities used for managing users, categories, transactions, and premium membership functionality.

---

## Database Tables

```text
Table users {
  id int [pk]
  username varchar
  email varchar
}

Table profile {
  id int [pk]
  user_id int [ref: - users.id]
  is_premium boolean
}

Table category {
  id int [pk]
  name varchar
  type varchar  // Income or Expense
  user_id int [ref: > users.id]
  created_at datetime
  updated_at datetime
}

Table transaction {
  id int [pk]
  user_id int [ref: > users.id]
  category_id int [ref: > category.id]
  amount decimal(10,2)
  date date
  description varchar
  created_at datetime
  updated_at datetime
}
```

---

## Entity Descriptions

### Users Table

The `users` table represents Django’s built-in authentication system, which manages registered users of the application.

Django authentication provides secure user registration, login/logout functionality, password management, and access control for user-specific financial data.

---

### Profile Table

The `profile` table stores premium membership information associated with each user.

Each user automatically receives a profile when their account is created using Django signals.

The `is_premium` field determines whether a user has access to premium budgeting functionality such as:

- Premium financial insights
- Transaction export functionality
- Advanced budgeting tools

This relationship is implemented as a one-to-one relationship between `users` and `profile`.

---

### Category Table

The `category` table stores user-created income and expense categories.

Each category belongs to a specific user, ensuring financial data remains separated between accounts.

Categories are used to organise transactions and improve filtering and reporting functionality.

---

### Transaction Table

The `transaction` table stores financial records created by users.

Each transaction belongs to:

- One user
- One category

Transactions include details such as:

- Amount
- Date
- Description
- Transaction category

This structure enables efficient financial tracking, filtering, and dashboard summary calculations.

---

## Entity Relationship Diagram (ERD)

The ERD below illustrates the database structure of the Freelancer Budget Tracker application and the relationships between entities.

![freelancer-budget-tracker-ERD](static/images/freelancer-budget-tracker-ERD.png "freelancer-budget-tracker-ERD")

---

## Relationship Summary

Relationships between entities in the Freelancer Budget Tracker application are as follows:

- A User can create many Categories
- A User can create many Transactions
- A Category can contain many Transactions
- Each Transaction belongs to exactly one User and one Category
- Each User has one associated Profile
- Each Profile belongs to exactly one User

---

## Database Design Overview

The relational database structure was designed to ensure:

- Secure user-specific financial management
- Clear ownership of data
- Efficient querying and filtering
- Separation of premium membership functionality
- Scalability for future financial features

The database relationships support the application's full CRUD functionality, dashboard summaries, filtering system, and premium feature access control.