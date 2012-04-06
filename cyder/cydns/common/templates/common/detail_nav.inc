<span class="nav-item">
    <a class="sub-link nav-link" href="{{ common.get_edit_url() }}">Edit</a>
</span>

{% if common.domain %}
    <span class="nav-item">
        <a class="sub-link nav-link" href="{{ common.domain.get_absolute_url() }}">View Domain</a>
    </span>
{% endif %}

{% if common.reverse_domain %}
    <span class="nav-item">
        <a class="sub-link nav-link" href="{{ common.reverse_domain.get_absolute_url() }}">View Reverse Domain</a>
    </span>
{% endif %}

<span class="nav-item">
    <a class="delete-link sub-link nav-link" href="{{ common.get_delete_url() }}">Delete</a>
</span>
