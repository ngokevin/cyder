{% from "tables.html" import render_table %}

<h1>{{ form_title }}</h1>

<table class="table">
    <thead>
        {% for item, value in common.details() %}
            <th>{{ item }}</th>
        {% endfor %}
    </thead>

    <tbody>
        <tr>
        {% for item, value in common.details() %}
            <td>{{ value }}</td>
        {% endfor %}
        </tr>
    </tbody>
</table>
