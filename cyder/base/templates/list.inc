<!-- Base generic title off of object's class name -->
<h1>{{ objects[0].__class__.__name__ + 's' }}</h1>

<!-- Basic bootstrap pagination -->
<div class="pagination">
    <ul>
        {% if page_obj.has_previous() %}
            <li>
                <a href="#">Prev</a></li>
        {% else %}
            <li class="disabled">
                <a href="#">Prev</a></li>
        {% endif %}
            </li>

        {% for page in range(1, page_obj.paginator.num_pages) %}
            {% if page == page_obj.number %}
                <li class="active">
                    <a href="#">{{ page_obj.number }}</a>
                </li>
            {% else %}
                <li><a href="?page={{ page }}">{{ page }}</a></li>
            {% endif %}
        {% endfor %}

        {% if page_obj.has_next() %}
            <li>
                <a href="?page={{ page_obj.next_page_number() }}">Next</a></li>
        {% else %}
            <li class="disabled">
                <a href="#">Next</a></li>
        {% endif %}
            </li>
    </ul>
</div>

<!-- Basic bootstrap table -->
<table class="table table-condensed table-striped">
    <thead>
    </thead>

    <tbody>
        {% for obj in objects %}
            <tr><td><a href='{{ obj.get_absolute_url() }}'>{{ obj }}</a></td></tr>
        {% endfor %}
    </tbody>
</table>
