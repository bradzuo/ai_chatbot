"""
drop table if exists CB_MS_TOPIC;
create table CB_MS_TOPIC
(
   ID_                  varchar(128) not null comment '时维编码',
   SCENES_ID_           varchar(128),
   PID_                 varchar(64),
   NAME_                varchar(512) comment '机构编码',
   LEVEL_               varchar(64),
   TENANT_ID_           varchar(64) comment '租户',
   CREATED_BY_ID_       varchar(64) comment '创建人ID',
   CREATED_BY_NAME_     varchar(64) comment '创建人名称',
   CREATED_TIME_        datetime comment '创建时间',
   DELFLAG_             varchar(1) comment '逻辑删除标记',
   DISPLAY_ORDER_       int comment '显示序号',
   MODIFIED_BY_ID_      varchar(64) comment '修改人ID',
   MODIFIED_BY_NAME_    varchar(64) comment '修改人名称',
   MODIFIED_TIME_       timestamp comment '修改时间',
   VERSION_             int comment '版本'
);
alter table CB_MS_TOPIC comment '主题信息表';

create table CB_MS_SCENES
(
   ID_                  varchar(128) not null comment '时维编码',
   NAME_                varchar(512) comment '机构编码',
   DESCRIBE_            varchar(512),
   TENANT_ID_           varchar(64) comment '租户',
   CREATED_BY_ID_       varchar(64) comment '创建人ID',
   CREATED_BY_NAME_     varchar(64) comment '创建人名称',
   CREATED_TIME_        datetime comment '创建时间',
   DELFLAG_             varchar(1) comment '逻辑删除标记',
   DISPLAY_ORDER_       int comment '显示序号',
   MODIFIED_BY_ID_      varchar(64) comment '修改人ID',
   MODIFIED_BY_NAME_    varchar(64) comment '修改人名称',
   MODIFIED_TIME_       timestamp comment '修改时间',
   VERSION_             int comment '版本'
);

create table CB_MS_INTENT
(
   ID_                  varchar(128) not null comment '时维编码',
   PID_                 varchar(128),
   STORY_ID_            varchar(128),
   INTENT_              varchar(2000) comment '{
            "key1":"什么是大额存单",
            "key2":"什么是个人大额存单",
            "key3":"大额存单是啥",
            ...
            }',
   REPLY_               varchar(2000) comment '{
            "key1":"大额存单是...",
            "key2":"...",
            ...
            }',
   TENANT_ID_           varchar(64) comment '租户',
   CREATED_BY_ID_       varchar(64) comment '创建人ID',
   CREATED_BY_NAME_     varchar(64) comment '创建人名称',
   CREATED_TIME_        datetime comment '创建时间',
   DELFLAG_             varchar(1) comment '逻辑删除标记',
   DISPLAY_ORDER_       int comment '显示序号',
   MODIFIED_BY_ID_      varchar(64) comment '修改人ID',
   MODIFIED_BY_NAME_    varchar(64) comment '修改人名称',
   MODIFIED_TIME_       timestamp comment '修改时间',
   VERSION_             int comment '版本',
   primary key (ID_)
);

create table CB_MS_STORIES
(
   ID_                  varchar(128),
   TOPIC_ID_            varchar(128),
   NAME_                varchar(512) comment '机构编码',
   TENANT_ID_           varchar(64) comment '租户',
   CREATED_BY_ID_       varchar(64) comment '创建人ID',
   CREATED_BY_NAME_     varchar(64) comment '创建人名称',
   CREATED_TIME_        datetime comment '创建时间',
   DELFLAG_             varchar(1) comment '逻辑删除标记',
   DISPLAY_ORDER_       int comment '显示序号',
   MODIFIED_BY_ID_      varchar(64) comment '修改人ID',
   MODIFIED_BY_NAME_    varchar(64) comment '修改人名称',
   MODIFIED_TIME_       timestamp comment '修改时间',
   VERSION_             int comment '版本',
   primary key (ID_)
);"""
