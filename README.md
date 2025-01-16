![your_repo_banner](link_to_your_banner)

# ```your_repository_name```

A one line summary of your repository

---

# Setup

1. Clone the repo:

    ```git clone git@github.com:communitiesuk/<your_repository_name>.git```

2. Enter the repo:

    ```cd <your_repository_name>```

3. Install the environment:

    ```conda env create -f environment.yml```

4. Activate the environment:

    ```conda activate <your_repository_name>```

5. Install pre-commit:

    ```pre-commit install```

6. Download the **'data'** folder ([from here](link_to_your_cloud_storage_here)) and add into the root directory of the repo.

7. Download the **'env'** file ([from here](link_to_your_cloud_storage_here)), add to the '/src' directory, and rename to '.env'.

8. Download the **'models'** folder ([from here](link_to_your_cloud_storage_here)) and add to the root directory of the repo.
---

To **UPDATE** an existing conda environment:

```conda env update --file environment.yml --prune```

---
