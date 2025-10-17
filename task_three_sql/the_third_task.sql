/* Task 1: Output the number of movies in each category, sorted descending */

SELECT
	c.name,
	COUNT(f.film_id) as films_amount
FROM
	film f
JOIN 
	film_category fc 
ON	
	fc.film_id = f.film_id 
JOIN
	category c
ON
	c.category_id  = fc.category_id
GROUP BY 	
	c.name
ORDER BY
	films_amount desc; 

/* Task 2: Output the 10 actors whose movies rented the most mONey was spent */

SELECT
	a.actor_id,
	a.last_name,
	a.first_name,
	count(r.rental_id),
	rank() over(ORDER BY count(r.rental_id) desc) rnk
FROM 	
	actor a
JOIN
	film_actor fa
ON
	fa.actor_id = a.actor_id
JOIN
	film f
ON	
	fa.film_id = f.film_id
JOIN	
	inventory i
ON
	i.film_id = f.film_id
JOIN
	rental r
ON
	r.inventory_id = i.inventory_id
GROUP BY
	a.actor_id,
	a.last_name,
	a.first_name
LIMIT
    10;

/* Task 3: Output the category of movies ON which the most mONey was spent */

SELECT
	c.name,
	sum(p.amount) as amount,
	rank() over(ORDER BY sum(p.amount) desc) rnk
FROM
	category c
JOIN
	film_category fc
ON
	fc.category_id = c.category_id
JOIN
	inventory i
ON
	i.film_id = fc.film_id
JOIN
	rental r
ON
	r.inventory_id = i.inventory_id
JOIN
	payment p
ON
	p.rental_id = r.rental_id
GROUP BY
	c.name
LIMIT
	1;

/* Task 4: Print the names of movies that are not in the inventory. Write a query WITHout using the IN operator. */

/* Query, using IN  */
SELECT
    f.film_id,
	f.title
FROM
	film f
WHERE
	f.film_id  NOT IN (
	
    SELECT
			i.film_id
		FROM
    
			inventory i 
	);

/* Query WITHout using IN */
SELECT
    f.film_id,
	f.title
FROM	
	film f 
LEFT JOIN
	inventory i
ON
	f.film_id = i.film_id
WHERE
	i.inventory_id IS NULL
ORDER BY
	f.title;
	
/* 
 * Task 5: Output the top 3 actors who have appeared the most in movies in the “Children” category.
 * If several actors have the same number of movies, output all of them.
 */

WITH actor_film_count AS (

SELECT
		a.first_name,
		a.last_name,
		count(*) AS amount,
		RANK() OVER(ORDER BY COUNT(*) desc) rnk
	FROM

		actor a 
	JOIN
		film_actor fa 
	ON
		fa.actor_id = a.actor_id 
	JOIN
		film_category fc 
	ON
		fc.film_id = fa.film_id 
	JOIN
		category c
	ON
		c.category_id = fc.category_id 
	WHERE
		c.name = 'Children'
	GROUP BY
		a.first_name,
		a.last_name
)

SELECT
	*
FROM
	actor_film_count afc
WHERE
	afc.rnk <= 3;

/* 
 * Task 6: Output cities WITH the number of active and inactive customers (active - customer.active = 1). 
 * Sort by the number of inactive customers in descending order. 
 */

SELECT
	ct.city,
	count(CasE WHEN c.active = 1 then 1 end) AS active_costumers,
	count(CasE WHEN c.active = 0 then 0 end) AS inactive_costunersalter 
FROM
	city ct
JOIN
	address a
ON
	a.city_id = ct.city_id
JOIN
	customer c
ON
	c.address_id = a.address_id
GROUP BY
	ct.city
ORDER BY
	inactive_costunersalter desc;

/* Task 7: Output the category of movies that have the highest number of total 
 * rental hours in the city (customer.address_id in this city) and that start 
 * WITH the letter “a”. Do the same for cities that have a “-” in them. Write everything in ONe query.
*/

/*
 * This way was the first, that came to my mind
 * It's less-effective, but I decided to leave it there :) 
*/

SELECT
	city_name,
	category_name,
	hours_spent
FROM
	
    SELECT
		ci.city AS city_name,
		ca.name AS category_name,
		ROUND((SUM(EXTRACT(HOUR FROM
     (r.return_date - r.rental_date)) + EXTRACT(DAY FROM
     (r.return_date - r.rental_date) * 24) + EXTRACT(MINUTE FROM
     (r.return_date - r.rental_date)) / 60)), 2) AS hours_spent,
		RANK() OVER(PARTITION BY ci.city ORDER BY SUM(EXTRACT(HOUR FROM
     (r.return_date - r.rental_date)) + EXTRACT(DAY FROM
     (r.return_date - r.rental_date) * 24) + EXTRACT(MINUTE FROM
     (r.return_date - r.rental_date)) / 60) DESC) AS rnk
	FROM
		rental r
	JOIN
		customer c
	ON
		c.customer_id = r.customer_id
	JOIN
		address a
	ON
		a.address_id = c.address_id 
	JOIN
		city ci
	ON
		a.city_id = ci.city_id 
	JOIN
		inventory i 
	ON
		r.inventory_id = i.inventory_id 
	JOIN
		film f 
	ON
		f.film_id = i.film_id 
	JOIN
		film_category fc
	ON
		fc.film_id = f.film_id
	JOIN
		category ca
	ON
		fc.category_id = ca.category_id
	WHERE
		ci.city LIKE 'a%' OR ci.city LIKE '%-%'
	GROUP BY
		ci.city,
		ca.name
	)	
WHERE 
	rnk = 1;

/*
 * The secONd ONe is more effective
 * Using EPOCH instead of calculating hours by extracting days, hours and minutes
 * This way is more accurate
*/

SELECT
	city_name,
	category_name,
	hours_spent
FROM
	(
    SELECT
		ci.city AS city_name,
		ca.name AS category_name,
		round(sum(extract(epoch FROM
     (r.return_date - r.rental_date))/3600), 2) AS hours_spent,
		rank() over(partitiON by ci.city ORDER BY sum(extract(epoch FROM
     (r.return_date - r.rental_date))/3600) desc) AS rnk
	FROM

		rental r
	JOIN
		customer c
	ON
		c.customer_id = r.customer_id
	JOIN
		address a
	ON
		a.address_id = c.address_id 
	JOIN
		city ci
	ON
		a.city_id = ci.city_id 
	JOIN
		inventory i 
	ON
		r.inventory_id = i.inventory_id 
	JOIN
		film f 
	ON
		f.film_id = i.film_id 
	JOIN
		film_category fc
	ON
		fc.film_id = f.film_id
	JOIN
		category ca
	ON
		fc.category_id = ca.category_id
	WHERE
		ci.city LIKE 'a%' OR ci.city LIKE '%-%'
	GROUP BY
		ci.city,
		ca.name
	)	
    WHERE 
	    rnk = 1;