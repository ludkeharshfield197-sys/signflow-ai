<template>
  <el-dialog
      :model-value="dialogVisible"
      @update:model-value="updateVisible"
      :title="dialogTitle"
      width="30%"
      @close="handleClose"
  >
    <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
    >
      <el-form-item label="模型名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>

      <el-form-item label="版本" prop="version">
        <el-input v-model="form.version" />
      </el-form-item>

      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio label="正常">正常</el-radio>
          <el-radio label="异常">异常</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="4" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="handleConfirm">确认</el-button>
        <el-button @click="handleClose">取消</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { defineEmits, defineProps, ref, watch } from "vue";
import requestUtil from "@/util/request";
import { ElMessage } from 'element-plus';

const props = defineProps(
    {
      id: {
        type: Number,
        default: -1,
        required: true
      },
      dialogTitle: {
        type: String,
        default: '',
        required: true
      },
      dialogVisible: {
        type: Boolean,
        default: false,
        required: true
      }
    }
);

const form = ref({
  id: -1,
  name: "",
  version: "",
  status: "正常",
  remark: "",
  size: "0MB",
  file_path: ""
});

const rules = ref({
  name: [
    { required: true, message: '请输入模型名称', trigger: 'blur' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' }
  ]
});

const formRef = ref(null);

const initFormData = async (id) => {
  try {
    const res = await requestUtil.get(`/modelYolo/action?id=${id}`);
    if (res.data.code === 200) {
      const modelData = res.data.data;
      form.value = {
        id: modelData.id,
        name: modelData.name,
        version: modelData.version,
        status: modelData.status,
        remark: modelData.remark,
        size: modelData.size,
        file_path: modelData.file_path
      };
    } else {
      ElMessage.error(res.data.message || '获取模型信息失败');
    }
  } catch (error) {
    console.error('获取模型信息失败:', error);
    ElMessage.error('获取模型信息失败');
  }
};

watch(
    () => props.dialogVisible,
    () => {
      let id = props.id;
      if (id !== -1) {
        initFormData(id);
      } else {
        form.value = {
          id: -1,
          name: "",
          version: "",
          status: "正常",
          remark: ""
        };
      }
    }
);

const emits = defineEmits(['update:modelValue', 'initModelList', 'update:dialogVisible']);

const handleClose = () => {
  emits('update:modelValue', false);
  emits('update:dialogVisible', false);
};

const updateVisible = (val) => {
  emits('update:dialogVisible', val);
};

const handleConfirm = () => {
  formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const isEdit = form.value.id !== -1;
        const result = await requestUtil.post("/modelYolo/save", {
          ...form.value,
          status: form.value.status || '正常'
        });
        if (result.data.code === 200) {
          ElMessage.success(isEdit ? "编辑成功！" : "新增成功！");
          formRef.value.resetFields();
          emits("initModelList");
          handleClose();
        } else {
          ElMessage.error(result.data.message || (isEdit ? '编辑失败' : '新增失败'));
        }
      } catch (error) {
        console.error('操作失败:', error);
        ElMessage.error('操作失败');
      }
    }
  });
};
</script>

<style scoped>
</style>