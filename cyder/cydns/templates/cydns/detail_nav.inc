<span class="nav-item">
    <a class="sub-link nav-link" href="{{ object.get_edit_url() }}">Edit</a>
</span>

{% if object.domain %}
    <span class="nav-item">
        <a class="sub-link nav-link" href="{{ object.domain.get_absolute_url() }}">View Domain</a>
    </span>
{% endif %}

{% if object.reverse_domain %}
    <span class="nav-item">
        <a class="sub-link nav-link" href="{{ object.reverse_domain.get_absolute_url() }}">View Reverse Domain</a>
    </span>
{% endif %}

<span class="nav-item">
    <a class="delete-link sub-link nav-link" href="{{ object.get_delete_url() }}">Delete</a>
</span>
