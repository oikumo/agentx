from agent_x.applications.web_ingestion_app.web_ingestion_app import WebIngestionApp

if __name__ == "__main__":
    app = WebIngestionApp()
    app.run(
        site_url = "https://www.verifone.cloud/docs/device-management/device-management-user-guide/",
        vectorstore_chroma_dir="sessions/web_ingestion/chroma_db_vf_device_management"

    )