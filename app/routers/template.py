
# ProjectModule Endpoints
@admin_router.post("/modules", response_model=ModuleAdminResponse)
async def create_module(module: ModuleCreateRequest, db: AsyncSession = Depends(get_db_async)):
    return await services.create_module(db, module)


@admin_router.get("/modules/{module_id}", response_model=ModuleAdminResponse)
async def get_module(module_id: str, db: AsyncSession = Depends(get_db_async)):
    return await services.get_module(db, module_id)


@admin_router.put("/modules/{module_id}", response_model=ModuleAdminResponse)
async def update_module(module_id: str, module: ModuleUpdateRequest, db: AsyncSession = Depends(get_db_async)):
    return await services.update_module(db, module_id, module)


@admin_router.delete("/modules/{module_id}", response_model=dict)
async def delete_module(module_id: str, db: AsyncSession = Depends(get_db_async)):
    return await services.delete_module(db, module_id)


@admin_router.post("/modules/{module_id}/set-template")
async def set_template_module(module_id: str, template_id: str,
                              db: AsyncSession = Depends(get_db_async)):
    try:
        return await services.set_template_module(db, module_id, template_id)
    except Exception as e:
        logging.error(f"Error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

