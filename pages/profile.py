"""
User Profile Page
"""

import streamlit as st

from database.user_queries import (
    update_user_profile,
    get_user_stats
)


def show_profile(user: dict):

    st.title("👤 My Profile")

    stats = get_user_stats(
        user["id"]
    )

    col1, col2 = st.columns([1, 2])

    with col1:

        st.image(
            "https://cdn-icons-png.flaticon.com/512/3135/3135715.png",
            width=180
        )

    with col2:

        st.subheader(
            user.get(
                "full_name",
                "User"
            )
        )

        st.write(
            f"📧 {user.get('email','')}"
        )

        st.write(
            f"🎯 Interviews Completed: {stats.get('total_interviews',0)}"
        )

        st.write(
            f"📊 Average Score: {stats.get('average_score',0)}%"
        )

    st.markdown("---")

    st.subheader(
        "Edit Profile"
    )

    full_name = st.text_input(
        "Full Name",
        value=user.get(
            "full_name",
            ""
        )
    )

    phone = st.text_input(
        "Phone Number",
        value=user.get(
            "phone",
            ""
        )
    )

    college = st.text_input(
        "College",
        value=user.get(
            "college",
            ""
        )
    )

    degree = st.text_input(
        "Degree",
        value=user.get(
            "degree",
            ""
        )
    )

    graduation_year = st.text_input(
        "Graduation Year",
        value=user.get(
            "graduation_year",
            ""
        )
    )

    target_role = st.text_input(
        "Target Role",
        value=user.get(
            "target_role",
            ""
        )
    )

    if st.button(
        "💾 Save Profile",
        use_container_width=True
    ):

        profile_data = {

            "full_name":
                full_name,

            "phone":
                phone,

            "college":
                college,

            "degree":
                degree,

            "graduation_year":
                graduation_year,

            "target_role":
                target_role

        }

        success = update_user_profile(

            user["id"],
            profile_data

        )

        if success:

            st.success(
                "Profile Updated Successfully"
            )

        else:

            st.error(
                "Profile Update Failed"
            )

