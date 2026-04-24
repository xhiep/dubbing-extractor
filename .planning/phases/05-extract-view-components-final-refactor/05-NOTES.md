# Phase 5: Extract View Components - Planning Notes

**Created**: 2026-04-24
**Status**: Ready for planning

## Goal
Tách 4 tabs UI ra thành view files riêng trong `src/views/`, giảm main.py từ ~2,527 dòng xuống ~400 dòng.

## Approach
- Tạo 4 view classes: SourceView, AdjustView, DubView, LogView
- Mỗi view class có method `build()` trả về configured frame
- Controllers sẽ wire events vào widgets từ views
- main.py chỉ còn: imports, window setup, view assembly

## Expected Structure After Phase 5

```
src/
  views/
    __init__.py
    source_view.py      # Tab "Nguồn" - input, buttons, step controls
    adjust_view.py      # Tab "Điều Chỉnh" - cover mode, blur params
    dub_view.py         # Tab "Lồng Tiếng" - TTS config, voice selection
    log_view.py         # Tab "Nhật Ký" - log display, progress bar
  controllers/          # Existing - event handlers
  modules/              # Existing - business logic
  components/           # Existing - reusable UI widgets
  utils/                # Existing - helpers

main.py                 # ~400 lines - window + view assembly only
```

## Key Decisions

### View Pattern
```python
class SourceView:
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.widgets = {}  # Store widget references for controller access
    
    def build(self) -> ttk.Frame:
        frame = ttk.Frame(self.parent)
        # Build UI layout
        # Store widgets in self.widgets
        return frame
    
    def get_widgets(self) -> dict:
        return self.widgets
```

### Integration with Controllers
```python
# In main.py
source_view = SourceView(notebook, config)
source_frame = source_view.build()
source_widgets = source_view.get_widgets()

source_controller = SourceController(source_widgets, config)
# Wire events
source_widgets['start_button'].config(command=source_controller.on_start_clicked)
```

## Risk Assessment

**Medium Risk** - Moving large UI code blocks
- Risk: Layout breaks, widgets not accessible
- Mitigation: Test each tab after extraction, verify all widgets work

## Success Criteria
- [ ] All 4 tabs extracted to separate view files
- [ ] main.py < 500 lines
- [ ] All tabs render correctly with proper layout
- [ ] All buttons/inputs work identically
- [ ] Controllers can access all widgets
- [ ] Config save/load still works
- [ ] Full pipeline test passes

## Next Steps
1. Run `/gsd-plan-phase 5` to create detailed plans
2. Execute plans sequentially
3. Test after each view extraction
4. Final integration test

## Notes
- Phase 5 là bước cuối cùng của refactoring
- Sau Phase 5, main.py sẽ giảm 87% so với ban đầu (3000 → 400 dòng)
- Complete MVC separation: Views (UI) → Controllers (events) → Modules (logic)
